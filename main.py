import praw
import os
import re
import remember as Remember
import log as Log
import atexit
import imgkit
import contentgen as ConGen
import threading
import time
from enum import Enum
from datetime import datetime
import signal
import sys
import util as Util



#imgkit.from_url('http://google.com', 'out.jpg')

Reddit = praw.Reddit("bot1")
Subreddit = Reddit.subreddit("all")
PostSubredditName = "ScreenCapResults"
PostSubreddit = Reddit.subreddit(PostSubredditName)

CommentQueue = []
ReplyQueue = []

LockComment = threading.Lock()
LockReply = threading.Lock()

OutDir = "out"

Running = True
Themes = {
	"light" : "css/light.css",
	"dark" : "css/dark.css",
	"common" : "css/common.css"
}

# Create out dir
if not os.path.isdir(OutDir):
	os.mkdir(OutDir)


class Reply():
	def __init__(self,SummonComment, Msg):
		self.SummonComment = SummonComment
		self.Msg = Msg

class LinkReply(Reply):
	def __init__(self,SummonComment, Link):
		RawMsg = "Find your picture on r/{0} at [{1}]({1})!"
		self.Link = Link
		super().__init__(SummonComment, RawMsg.format(PostSubredditName, Link))

class ErrorReply(Reply):
	def __init__(self,SummonComment, Err):
		super().__init__(SummonComment, str(Err))


# Thread to read through all the new comments and add them to the stack
def ReadComments():
	global LockComment
	global CommentQueue
	for SummonComment in Subreddit.stream.comments():
		print(SummonComment.body)
		#print("[ReadComments]: " + str(Running))
		if re.search(Util.TriggerKeyword, SummonComment.body, re.IGNORECASE) and Util.CommentExists(SummonComment.id, Reddit):
			if not Remember.IsReplied(SummonComment.id):
				Remember.AddReplied(SummonComment.id)

				LockComment.acquire()
				CommentQueue.append(SummonComment)
				LockComment.release()

				Log.Good("Found a summon comment: " + SummonComment.id)

# Seperate thread to gen images
def ContentGen():
	global LockComment
	global LockReply
	global CommentQueue
	global ReplyQueue
	while True:
		#print("[Content Gen]: " + str(Running))
		if len(CommentQueue) > 0:
			# Get the summon comment
			LockComment.acquire()
			SummonComment = CommentQueue.pop()
			LockComment.release()

			Log.Info(SummonComment.id + " has made it to the CONTENT GEN stage")

			try:
				

				# Get the options from the summon comment
				# try:
				Options = Util.ProcessCommentsArgs(SummonComment.body)
				
				# Get an set the theme of the image
				CssTheme = [Themes["common"], Themes[Options["Theme"]]]
				#print(str(CssTheme))
				#ImgFile = OutDir + "/" + SummonComment.id + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +".jpg" 
				ImgFile = OutDir + "/" + SummonComment.id + ".jpg"
				# Get the comments to display on the image
				Comment = None
				IncludePost = True

				if Options["Target"] == "parent-post":
					Comment = Util.GetParentComment(SummonComment, Reddit)
				elif Options["Target"] == "current-post":
					Comment = SummonComment
				elif Options["Target"] == "current":
					Comment = SummonComment
					IncludePost = False
				elif Options["Target"] == "parent":
					Comment = Util.GetParentComment(SummonComment, Reddit)
					IncludePost = False
				else:
					Log.Bad("No target detected: " + Options["Target"])
					raise Exception("Oh no! I could not recognise the -target field, did you mean -target current-post?")

				#print(str(Comment))

				# Gen img data
				CommentDataIn = ConGen.CommentData(Comment, Comment.author)
				
				# Construct the image
				PostDataIn = None
				if IncludePost:
					PostDataIn = ConGen.PostData(Comment.submission, Comment.submission.author)
				#print(str(PostDataIn))
				AuthorDataIn = ConGen.AuthorData(Comment.author)
				RenderHtml = ConGen.ConstructHTML(PostDataIn, 
					[CommentDataIn], 
					ConGen.AuthorData(SummonComment.author))

				imgkit.from_string(RenderHtml, ImgFile, css=CssTheme)

				# Add the reply msg to the reply stack
				LockReply.acquire()
				ReplyQueue.append(LinkReply(SummonComment, ImgFile))
				LockReply.release()
			except Exception as e:
				Log.Bad(str(e))

				LockReply.acquire()
				ReplyQueue.append(ErrorReply(SummonComment,e))
				LockReply.release()

				#break

# Seperate thread to send reply msgs
def ReplyManager():
	global LockReply
	global ReplyQueue
	while True:
		if len(ReplyQueue) > 0:

			LockReply.acquire()
			CurrentReply = ReplyQueue.pop()
			LockReply.release()

			Log.Info(CurrentReply.SummonComment.id + " has made it to the REPLY stage")

			#print(str(CurrentReply))
			# Determine type and react
			if type(CurrentReply) is LinkReply:
				Post = PostSubreddit.submit_image(CurrentReply.SummonComment.id, CurrentReply.Link)
				NewLink = LinkReply(CurrentReply.SummonComment, Post.permalink)
				CurrentReply.SummonComment.reply(NewLink.Msg)
				Log.Good(CurrentReply.SummonComment.id + " has had a reply: " + NewLink.Msg)
			elif type(CurrentReply) is ErrorReply or type(CurrentReply) is Reply:
				CurrentReply.SummonComment.reply(CurrentReply.Msg)
				Log.Bad(CurrentReply.SummonComment.id + " has had a error: " + CurrentReply.Msg)
			else:
				Log.Bad("Unknown Reply Type!")


# Boot
Remember.InitReplied()
atexit.register(Remember.WriteReplied)

#ReadComments()
#ContentGen()

threading.Thread(target=ReadComments, name='ReadComments', daemon=True).start()
#threading.Thread(target=ReadComments, name='ReadComments', daemon=True).start()
#threading.Thread(target=ReadComments, name='ReadComments', daemon=True).start()
threading.Thread(target=ContentGen, name='ContentGen', daemon=True).start()
threading.Thread(target=ReplyManager, name='ReplyManager', daemon=True).start()



# Now start both threads
#ReadComments()
#ReadComments.start()


# def MakeImg(Comment, SummonAuthor):
# 	try :
# 		CommentDataIn = ConGen.CommentData(Comment, Comment.author)
# 		PostDataIn = ConGen.PostData(Comment.submission, Comment.submission.author)
# 		AuthorDataIn = ConGen.AuthorData(Comment.author)
# 		RenderHtml = ConGen.ConstructHTML(PostDataIn, [CommentDataIn,CommentDataIn,CommentDataIn], AuthorDataIn)

# 		css = ["css/common.css","css/dark.css"]
# 		imgkit.from_string(RenderHtml, 'out.png', css=css)

# 	except AttributeError as e:
# 		Log.Bad("No name found: " + str(e))

def signal_handler(signal, frame):
	#global Running
	#global A
	#global B
	#print("Exiting")
	#Running = False
	#A.join(600)
	#B.join(600)
	#LockComment.acquire()
	#LockComment.release()
	sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while Running:
	pass
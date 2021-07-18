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
import config

#imgkit.from_url('http://google.com', 'out.jpg')
CommentQueue = []
ReplyQueue = []

LockComment = threading.Lock()
LockReply = threading.Lock()



Running = True

# Create out dir
if not os.path.isdir(config.OutDir):
	os.mkdir(config.OutDir)


class Reply():
	def __init__(self,SummonComment, Msg):
		self.SummonComment = SummonComment
		self.Msg = Msg

# The reply calss for sucessfule replies
class LinkReply(Reply):
	def __init__(self,SummonComment, Link, Sub):
		RawMsg = "Find your picture on r/{0} at [{1}]({1})!"
		self.Link = Link
		self.Sub = Sub
		super().__init__(SummonComment, RawMsg.format(Sub, Link))

# Error reply class
class ErrorReply(Reply):
	def __init__(self,SummonComment, Err):
		super().__init__(SummonComment, "ERR - " + str(Err))


# Thread to read through all the new comments and add them to the stack
def ReadComments():
	global LockComment
	global CommentQueue
	for SummonComment in config.ReadSubreddit.stream.comments():
		#print(SummonComment.body)
		#print("[ReadComments]: " + str(Running))
		if re.search(config.TriggerKeyword, SummonComment.body, re.IGNORECASE) and Util.CommentExists(SummonComment.id, config.Reddit):
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
				try:
					CssTheme = [config.Themes["common"], config.Themes[Options["Theme"]]]
				except Exception as e:
					raise Exception("Invalid Theme: " + str(e))
				#print(str(CssTheme))
				#ImgFile = config.OutDir + "/" + SummonComment.id + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +".jpg" 
				ImgFile = config.OutDir + "/" + SummonComment.id + ".jpg"
				# Get the comments to display on the image
				Comment = None
				IncludePost = True

				# Determine which post to capture
				if Options["Target"] == "parent-post":
					Comment = Util.GetParentComment(SummonComment, config.Reddit)
				elif Options["Target"] == "current-post":
					Comment = SummonComment
				elif Options["Target"] == "current":
					Comment = SummonComment
					IncludePost = False
				elif Options["Target"] == "parent":
					Comment = Util.GetParentComment(SummonComment, config.Reddit)
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
				ReplyQueue.append(LinkReply(SummonComment, ImgFile, Options["PostSubreddit"]))
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
				# Post the image on the sub in the link reply
				try:
					#print(type(CurrentReply.Sub));
					PostSub = config.Reddit.subreddit(CurrentReply.Sub)
					Post = PostSub.submit_image(CurrentReply.SummonComment.id, CurrentReply.Link)

					# Send the reply
					NewLink = LinkReply(CurrentReply.SummonComment, Post.permalink, CurrentReply.Sub)
					CurrentReply.SummonComment.reply(NewLink.Msg)
					Log.Good(CurrentReply.SummonComment.id + " has had a reply: " + NewLink.Msg)
				except Exception as e:
					Log.Bad(str(e))
					#if type(Exception) != praw.exceptions.RedditAPIException:
					LockReply.acquire()
					ReplyQueue.append(ErrorReply(CurrentReply.SummonComment,e))
					LockReply.release()
				

				
			elif type(CurrentReply) is ErrorReply or type(CurrentReply) is Reply:

				# if it is a error
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
	Remember.WriteReplied
	sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while Running:
	pass
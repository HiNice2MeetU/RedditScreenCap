import log as Log
import os
import config

# Write the post replied array on shutdown
def WriteReplied():
	Log.Good("Writing Comments Posts")
	with open(config.RepliedFileStorage, "w") as File:
		for Post in PostReplied:
			File.write(Post + "\n")
	Log.Info("Loaded Comments Replied: " + str(PostReplied))

# Read the replied comments if file exists
def InitReplied():
	# AHH Global 
	global PostReplied

	if os.path.isfile(config.RepliedFileStorage):
		with open(config.RepliedFileStorage, "r") as File:
			ReadFile = File.read()
			SplitFile = ReadFile.split("\n")
			
			PostReplied = list(filter(None, SplitFile))

			Log.Good("Reading Replied Comments")
	else:
		#PostReplied = []
		File = open(config.RepliedFileStorage, "x")
		File.close()

# Check if has been replied too
def IsReplied(Id):
	return Id in PostReplied

# Declare a post/comment replied to
def AddReplied(Id):
	global PostReplied

	#print("adding reply")

	for item in PostReplied:
		#print("Iterate")
		if item == Id:
			return

	PostReplied.append(Id)


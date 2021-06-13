import praw
from prawcore.exceptions import NotFound

TriggerKeyword = "!ScreenCap"

def CommentExists(id, Reddit):
    try:
        Reddit.comment(id).id
    except NotFound:
        return False
    return True

def GetParentComment(SummonComment, Reddit):
	ParentID = SummonComment.parent_id
	if ParentID.startswith("t3_"):
		raise Exception("Cannot render the parent of a top level comment, try using -target current_post")
	else:
		
		ParentID = ParentID.removeprefix("t1_")
		#print(ParentID)
		Comment = Reddit.comment(id = ParentID)
		Comment.refresh()
		return Comment

# Process the comment args
def ProcessCommentsArgs(Text):
	Return = {
		"Theme" : "dark",
		"Delivery" : "comment",
		"Target" : "parent-post"
	}

	SplitText = Text.split(" ")
	index = None

	# Find the index of TriggerKeyword
	for i in range(0,len(SplitText)):
		Section = SplitText[i]
		SplitText.pop(0)
		if Section == TriggerKeyword:
			index = i
			break

	if index == None:
		raise Exception("No trigger keyword found!")
	

	# Get options
	#print(str(SplitText))
	for e in range(0,len(SplitText)):
		Section = SplitText[e]
		

		if Section == "-theme":
			# Set theme
			NextSection = SplitText[e + 1]
			Return["Theme"] = NextSection

		elif Section == "-target":
			# Set the target (eg. the parent comment or child comment)
			NextSection = SplitText[e + 1]
			Return["Target"] = NextSection
		elif Section == "-delivery":
			# Set the deliver (eg. post on sub or comment link)
			if NextSection == "subreddit":
				Return["Delivery"] = "post"
				Return["PostSubreddit"] = SplitText[e + 2].replace('r/', '')

	return Return
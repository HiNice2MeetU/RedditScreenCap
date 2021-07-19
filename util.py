import praw
import config
from prawcore.exceptions import NotFound



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
		"PostSubreddit" : config.PostSubredditName,
		"Target" : "current-post"
	}

	SplitText = Text.split()
	index = None

	# Find the index of TriggerKeyword
	for i in range(0,len(SplitText)):
		Section = SplitText[i]
		SplitText.pop(0)
		if Section == config.TriggerKeyword:
			index = i
			break

	if index == None:
		raise Exception("No trigger keyword found!")

	# Get options
	#print(str(SplitText))
	for e in range(0,len(SplitText)-1):
		Section = SplitText[e]
		NextSection = SplitText[e + 1]

		#print(NextSection)

		if Section == "-theme":
			# Set theme
			Return["Theme"] = NextSection

		elif Section == "-target":
			# Set the target (eg. the parent comment or child comment)
			Return["Target"] = NextSection
		elif Section == "-subreddit":
			# If used will post image on other sub than the default post
			Return["PostSubreddit"] = NextSection.replace('r/', '')

	return Return
import praw
# Reddit instance
Reddit = praw.Reddit("bot1")
Reddit.validate_on_submit = True

# The default ReadSubreddit to read all posts from
ReadSubreddit = Reddit.subreddit("MyTestSubredditHi")

# The default PostSubreddit to put images
PostSubredditName = "ScreenCapResults"

# The dir to put images
OutDir = "out"

# Specify your themes and their css file
Themes = {
	"light" : "css/light.css",
	"dark" : "css/dark.css",
	"common" : "css/common.css"
}

# Trigger keyword to summon bot
TriggerKeyword = "!ScreenCap"

# File containing post ids we've been to
RepliedFileStorage = "PostsReplied.txt"
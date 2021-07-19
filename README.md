# RedditScreenCap

## A small bot to automatically take a screenshot of a comment and post it somewhere!

This was really just an excuse for me to finally learn some python but whatever...

### How does it work
It simpiles gets your comment from the reddit api (using praw) and renders the html (using imgkit) to a image then posts it on the sub of your choice!


### Results
![Img-Dark](https://raw.githubusercontent.com/HiNice2MeetU/RedditScreenCap/main/display/img-dark.jpg "Img-Dark")

![Comment-Light](https://raw.githubusercontent.com/HiNice2MeetU/RedditScreenCap/main/display/comment-light.jpg "Comment-Light")

![Link-Dark](https://raw.githubusercontent.com/HiNice2MeetU/RedditScreenCap/main/display/link-dark.jpg "Link-Dark")


### How to use!

Make a new comment under a post or comment then type...

!ScreenCap \<flags\>

#### Flags

|Flag |Options                           | default       |
|-----|----------------------------------|---------------|
|!ScreenCap | Needed to invoke bot | n/a
|-theme| light, dark                      | light         | 
|-target| parent-post, current-post, post, current | parent-post |
|-subreddit | \<name of subreddit\> | r/ScreenCapResults |

##### Target parent-post and parent are only usable if your comment is not a top level comment



#### Options in Config.py
|Var | Does                              | Default       |
|----|-----------------------------------|---------------|
|ReadSubreddit| Specifies the subreddit to search for invokations | r/MyTestServerHi |
|PostSuredditName | Specifies the default subreddit to post result images on | r/ScreenCapResults |
|OutDir | Location to locally store the output images | out |
|TriggerKeyword | Specifies the trigger keyword need to invoke bot | !ScreenCap |
|RepliedFileStorage | File containing all the comments it has replied too | PostsReplied.txt |

#### External packages used
- atexit
- imgkit
- praw
- markdown
- requests

built in python!

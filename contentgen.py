import markdown
import requests
import log as Log

def IsUrlImage(ImageUrl):
	ImageFormats = ("image/png", "image/jpeg", "image/jpg")
	

	try:
		R = requests.head(ImageUrl)
		if "content-type" in R.headers:
			if R.headers["content-type"] in ImageFormats:
				return True
		else:
			raise AttributeError("Return does not have content-type header")
	except requests.exceptions.SSLError as e:
		Log.Bad("SSL Err: " + str(e))
	except AttributeError as i:
		Log.Bad(str(i))
	except requests.exceptions.MissingSchema as t:
		Log.Bad("Invalid URL: " + str(t))
	return False

# A class that has the data on authors
class AuthorData:
	def __init__(self, Author):
		self.AuthorName = Author.name
		try:
			if hasattr(Author, 'icon_img'):
				if Author.icon_img != "https://styles.redditmedia.com/t5_1yz875/styles/profileIcon_klqlly9fc4l41.png?width=256&height=256&crop=256:256,smart&s=94486fc13b9ca9e154e9e8926e3d8c43ccc80be3":
					self.AuthorPic = Author.icon_img
				else:
					raise Exception("Not supported icon")

				#print(Author.icon_img)
			else:
				raise Exception("No Icon")
		except (Exception) as e:
			self.AuthorPic = "https://via.placeholder.com/28"
			Log.Bad("No pfp found: " + str(e))

# A class holding all the necessary data to draw a comment
class CommentData():
	def __init__(self, Comment, Author):
		self.BodyHtml = Comment.body_html
		self.Author = AuthorData(Author)
		

# A class holding all the necessary data to draw a post
class PostData():
	def __init__(self, Submission, Author):
		self.Title = Submission.title
		self.Author = AuthorData(Author)

		# Get body
		if not Submission.selftext == "":
			# If post contains text
			self.BodyHtml = markdown.markdown(Submission.selftext)
		else:
			# If post constains url
			if IsUrlImage(Submission.url):
				self.BodyHtml = "<img class=\"center\" style=\"max-width:300px; width:100%; \" src=\"" + Submission.url + "\" alt=\"" + Submission.url +"\">"
			else:
				self.BodyHtml = "<a href=\"" + Submission.url + "\">" + Submission.url + "</a>"

		
		

# Create a div that displays a comment
def _ConstructCommentHTML_(Data, __Shift__ = 0):
	FakeReturn = """
<div class="comment" style="margin-left: {2}px">

{1}
	
{0}

</div>

"""
	RealReturn = FakeReturn.format(Data.BodyHtml, 
		_ConstructAuthorHTML_(Data.Author), 
		__Shift__ * 50)

	#print(RealReturn)
	return RealReturn

# Create a div that displays a post
def _ConstructPostHTML_(Data):
	FakeReturn = """
<div class="post">

{2}

<!-- Title -->
<h2> {0} </h2>

{1}

</div>
<br>
"""
	RealReturn = FakeReturn.format(Data.Title, 
		Data.BodyHtml, 
		_ConstructAuthorHTML_(Data.Author))

	#print(RealReturn)
	return RealReturn

# Create a div that displays a user
def _ConstructAuthorHTML_(Data, __Credit__ = False):
	FakeReturn = """
<!-- Author and pfp -->
<div class={3} style="text-align: left;">
	<img style="vertical-align:middle; width:28px;height:28px;" src="{1}" alt="Author's pfp">
	<span style="vertical-align:middle; font-size: small;">{2}{0}</span>
</div>
"""
	if __Credit__:
		RealReturn = FakeReturn.format(Data.AuthorName, 
			Data.AuthorPic, 
			"Created by ScreenCapBot_1 • Summoned by ",
			"credit author")
	else:
		RealReturn = FakeReturn.format(Data.AuthorName, Data.AuthorPic, "", "author")
	#print(RealReturn)
	return RealReturn

def ConstructHTML(PostData, CommentDataArr, AuthorData ):
	Return = ""
	if not PostData == None:
		Return = _ConstructPostHTML_(PostData)

	index = 0
	ClassName = CommentDataArr.__class__.__name__

	# Check what class is class name
	if ClassName == "list":
		# Assume it is a list of comment data
		for CommentData in CommentDataArr:
			index += 1
			Return = Return + _ConstructCommentHTML_(CommentData)

	Return = Return + _ConstructAuthorHTML_(AuthorData, True)

	#print(Return)
	return Return


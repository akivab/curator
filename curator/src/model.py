"""
Manages the models for the curator webapp
@since: February 26, 2012
@author: akivab
"""
from google.appengine.api import images, users
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from hashlib import md5
  
class LinkedData(db.Model):
  # data held by this link
  data = db.BlobProperty()
  # type
  type = db.StringProperty()
  # md5 hash
  hash = db.StringProperty()
  # link (in case we don't want to store data)
  link = db.StringProperty()
  
  @classmethod
  def add_data(cls, **kwargs):
    try:
      tmp = cls(**kwargs)
      tmp.put()
      return tmp
    except Exception:
      return None
      
class UserData(db.Model):
  """We store users as a UserData object. Contains a user's info, currently
  using the db.UserProperty() for identification and nickname() for name."""
  # the user's google user property
  google_id = db.UserProperty()
  # the name of the user
  name = db.StringProperty()
  # date joined
  joined = db.DateProperty(auto_now_add=True)
  # people this guy/gal follows
  following = db.ListProperty(db.Key)
  # people following this guy/gal
  followers = db.ListProperty(db.Key)
  # picture of this person
  picture = db.ReferenceProperty(LinkedData)
  @classmethod
  def add_or_get_user(cls):
    user = users.get_current_user()
    if not user:
      return None
    user_data = UserData.gql("WHERE google_id=:1", user).get()
    if not user_data:
      user_data = UserData(google_id=user, name=user.nickname())
      user_data.put()
    return user_data
    
    
class Post(polymodel.PolyModel):
  """Votable content (includes comments, posts, content, groups of content)"""
  # the number of points a votable item has
  points = db.IntegerProperty()
  # the voters of a particular votable item
  voters = db.ListProperty(db.Key)
  # the user sharing the content
  user = db.ReferenceProperty(UserData)
  # the datetime content was added
  added = db.DateTimeProperty(auto_now_add=True)
  # the datetime content was modified
  modified = db.DateTimeProperty(auto_now=True)
    
class Content(Post):
  """Content that will be shared"""
  # the content being shared
  data = db.ReferenceProperty(LinkedData, collection_name="content_data_set")
  # a thumbnail for the content being shared (for music, not the same)
  image = db.ReferenceProperty(LinkedData, collection_name="image_data_set")
  # title of the data being shared
  title = db.StringProperty()
  # the artist of the data
  artist = db.StringProperty()
  # a description of the data
  description = db.StringProperty()

  @classmethod
  def add_image(cls, origin=None, data=None, type=None, user=None):
    """We get origin link, data, and type"""
    DEFAULT_TITLE = 'image'
    DEFAULT_DESCRIPTION = 'no description'
        
    if not type or not user:
      return None
    md5_hash = md5(data).hexdigest()
    
    original = LinkedData.gql("WHERE type=:1 AND hash=:2", type, md5_hash).get()
    if not original:
      original = LinkedData.add_data(type=type, data=data, hash=md5_hash, link=origin)
    content = Content.gql("WHERE data=:1", original).get()
    if not content:
      content = Content(data=original,
                        image=original,
                        user=user,
                        artist=user.name,
                        title=DEFAULT_TITLE,
                        description=DEFAULT_DESCRIPTION)
      content.put()
    return content
  
  @classmethod
  def add_music(cls, origin=None, data=None, title=None, artist=None, image=None, type=None, user=None):
    DEFAULT_DESCRIPTION='no description'
    if not user: return None
    md5_hash = 'music_without_data'
    if data: md5_hash = md5(data).hexdigest()
    
    original = LinkedData.gql("WHERE type=:1 AND hash=:2", type, md5_hash).get()
    if not original:
      original = LinkedData.add_data(type=type, data=data, hash=md5_hash, link=origin)
    
    content = Content.gql("WHERE artist=:1 AND title=:2 AND data=:3", artist, title, original).get()
    if not content:
      content = Content(data=original,
                        image=image,
                        user=user,
                        artist=artist,
                        title=title,
                        description=DEFAULT_DESCRIPTION)
      content.put()
    return content
  
class Comment(Post):
  """A comment object"""
  # the parent comment of this comment
  parent_post = db.SelfReferenceProperty(collection_name="parent_post_set")
  # the comment text of this comment
  comment_text = db.TextProperty()
  # the commentor of this comment
  commentor = db.ReferenceProperty(UserData)
  # the comments for this content
  comments = db.SelfReferenceProperty(collection_name="sub_comment_set")

class SinglePost(Post):
  """A post object. Either original or reshared content"""
  # parent is null if this is original content, link to shared if reshared
  parent_post = db.ReferenceProperty(Post, collection_name="parent_post_set")
  # the original content (none, if this is original)
  original_post = db.ReferenceProperty(Post, collection_name="original_post_set")
  # the comments for this content
  comments = db.ReferenceProperty(Comment)
  # the content being shared
  content = db.ReferenceProperty(Content)
  
  @classmethod
  def get_similar(cls, **kwargs):
    """Returns similar posts of this post"""
    original = kwargs.get('original')
    siblings = []
    if original:
      siblings = Post.gql("WHERE original=:1", original.key()).fetch(100)
    return siblings

class GroupPost(Post):
  """A group of posts."""
  # a list of posts (each a post object)
  posts = db.ListProperty(db.Key)
  # the comments for this content
  comments = db.ReferenceProperty(Comment)
  

"""
A set of utilities, including error defintions
@since: Feb 27, 2012
@author: akivab
"""
from __future__ import with_statement
from google.appengine.api import urlfetch, users, images
from google.appengine.api.urlfetch_errors import InvalidURLError
from hashlib import md5
from model import Content, LinkedData, UserData
from urllib import quote_plus
import base64
import re


class TypeNotFoundException(Exception): pass
class FieldNotFoundException(Exception): pass
class UserNotFoundException(Exception): pass
class ContentNotAddedException(Exception): pass
class ImageNotFoundException(Exception): pass

def decode_base64_image(data):
  regex = re.search('base64,(.+)', data)
  if regex:
    image_data = regex.group(1)
    return base64.b64decode(image_data)
  return None

def get_image_type(link):
  result = re.search(r'(image\/)(png|gif|jpg|jpeg)', link)
  try:
    if not result:
      linkedResult = urlfetch.fetch(link)
      if linkedResult.status_code != 200: return None
      contentType = linkedResult.headers['content-type']
      result = re.search(r'(image\/)(png|gif|jpg|jpeg)', contentType)
    return result.group(2)
  except InvalidURLError:
    return None
  return None
    

def add_image(link=None, data=None):
  if not link and not data:
    raise FieldNotFoundException('no link or data found when adding image')
  image_content = None
  if not data:
    result = urlfetch.fetch(link)
    if result.status_code != 200:
      raise ImageNotFoundException('image %s not found' % str(link))
    image_content = result.content
    image_type = get_image_type(link)
  else:
    image_content = decode_base64_image(data)
    image_type = get_image_type(data)
    link = 'binary data'
    
  if image_content:
    content_key = Content.add_image(origin=link,
                                    data=image_content,
                                    type=image_type,
                                    user=UserData.add_or_get_user())
    return content_key
  return None

def add_music(link=None, title=None, artist=None):
  cover_art = get_cover_art(title, artist)
  music = get_music_file(link, True)
  music_content = music[0] if music else None
  type = music[1] if music else None
    
  content_key = Content.add_music(origin=link,
                                  artist=artist,
                                  title=title,
                                  data=music_content,
                                  image=cover_art,
                                  user=UserData.add_or_get_user(),
                                  type=type if type else 'music')
  return content_key

def get_music_file(link, wants_result_obj=False):
  try:
    result = urlfetch.fetch(link)
    if result.status_code == 200:
      mp3_content = result.content
      if wants_result_obj: return mp3_content, result.headers.get('content-type')
      return mp3_content
  except Exception: pass
  return None

def resize(image):
  return images.resize(image, width=200)

def get_cover_art(title, artist):
  link = get_cover_art_link(title,artist)
  image = LinkedData.gql("WHERE link=:1", link).get()
  if image: return image
  
  result = urlfetch.fetch(link)
  if result.status_code == 200:
    img = resize(result.content)
    type = result.headers.get('content-type')
    image = LinkedData(type=type, data=img, hash=md5(img).hexdigest(), link=link)
    image.put()
    return image
  return None

def get_cover_art_link(title, artist):
  format = 'http://ws.audioscrobbler.com/2.0/?method=%s&artist=%s&track=%s&api_key=%s'
  key = 'b89d099447a7cb2bfb3aacc5aecf7b96'
  artist = quote_plus(artist)
  title = quote_plus(title)
  link = format % ('track.getinfo', artist, title, key)
  link2 = format % ('artist.getimages', artist, title, key)
  result = urlfetch.fetch(link)
  if result.status_code == 200:
    img = get_image_from_xml(result.content)
    if img: return img
  result = urlfetch.fetch(link2)
  if result.status_code == 200:
    img = get_image_from_xml(result.content)
    if img: return img
  return None

def get_image_from_xml(image_content):
    result = re.search(r'size name="(original|medium)"[^>]+>([^<]+)', image_content)
    if result:
      return result.group(2)
    return None
        
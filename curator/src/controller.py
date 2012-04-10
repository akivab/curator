"""
Manages the controllers for the curator webapp
@since: February 26, 2012
@author: akivab
"""
from google.appengine.api import urlfetch, users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson
from model import *
from utilities import *
import os
import logging
import re


class DataHandler(webapp.RequestHandler):
  """Handles data coming in. Only for post requests.
    Checks if user is signed in and deals with getting data from server"""
  def post(self):
    """@return: JSON string with data about post
    Data comes into a post request with the following fields:
      type (Image, Screenshot, or Music)
      data (for screenshots)
      title (for songs)
      artist (for songs)
      link (for images, songs)"""
      
    type = self.request.get('type')
    self.user = users.get_current_user()
    try:
      if not self.user:
        raise UserNotFoundException('no user was signed in!')
      if type not in ['image', 'screenshot', 'music']:
        raise TypeNotFoundException('type %s not found' % type)
      to_return = self.process_data(type)

    except Exception, e:
      logging.log(logging.DEBUG, str(e))
      to_return = {'error' : str(e)}
    self.response.out.write(simplejson.dumps(to_return))
  
  def process_data(self, type):
    content_key = None
    if type == 'image':
      link = self.request.get('link')
      data = self.request.get('data')
      if not link and not data:
        raise FieldNotFoundException('no link or no data attached with image')
      if not link:
        content_key = add_image(data=data)
      else:
        content_key = add_image(link=link)
    elif type == 'screenshot':
      data = self.request.get('data')
      if not data:
        raise FieldNotFoundException('no data attached with screenshot')
      content_key = add_image(data=data)
    elif type == 'music':
      link = self.request.get('link')
      title = self.request.get('title')
      artist = self.request.get('artist')
      if not link or not title or not artist:
        raise FieldNotFoundException('not all fields set for music')
      content_key = add_music(link=link, title=title, artist=artist)
    if content_key:
      return {'type': type,
              'content_key': str(content_key.key()), 
              'content_image_key': str(content_key.image.key()),
              'content_artist': content_key.artist, 
              'content_title': content_key.title,
              'content_description': content_key.description
              }
    raise ContentNotAddedException('content for type %s not added' % type)

class MainPage(webapp.RequestHandler):
    def get(self):
      template_values = {}
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

class UserHandler(webapp.RequestHandler):
    def get(self):
      is_signed_in = (users.get_current_user() != None)
      if is_signed_in:
        val = {'is_signed_in': True,
               'name': users.get_current_user().nickname(),
               'logout_url': users.create_logout_url("/")}
      else:
        val = {'is_signed_in': False,
               'login_url': users.create_login_url("/"),
               'image':self.request.host + "/img/login_img.png"}
      self.response.out.write(simplejson.dumps(val))
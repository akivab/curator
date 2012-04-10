"""
The main point of entry for the webapp
@since: February 26, 2012
@author: akivab
"""
from controller import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/data', DataHandler),
  ('/test', UserHandler),
], debug=True)


def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

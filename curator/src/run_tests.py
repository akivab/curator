"""
Tests the controller for the curator webapp
@since: February 26, 2012
@author: akivab
"""

from google.appengine.api import apiproxy_stub_map, datastore_file_stub, \
  urlfetch_stub, images
from google.appengine.ext import testbed
from utilities import decode_base64_image, resize, get_image_type, \
  get_image_from_xml, get_music_file, get_cover_art_link, add_music, add_image
import os
import unittest



TEST_IMAGE_LINK = "http://the-curator.appspot.com/test_data/image.png"
TEST_MP3 = "http://the-curator.appspot.com/test_data/song.mp3"
TEST_MP3_ARTIST = "David Guetta"
TEST_MP3_SONG_TITLE = 'Titanium (Feat. Sia)'
TEST_MP3_IMAGE_XML = """

<?xml version="1.0" encoding="utf-8"?>
<lfm status="ok">
<images artist="Couer de Pirate" page="1" perPage="50" totalPages="2" total="56">
            <image>
        <title>PNG</title>    self.assertEqual(img.format, images.PNG)

        <url>http://www.last.fm/music/C%C5%93ur+de+Pirate/+images/54238609</url>
        <dateadded>Wed, 10 Nov 2010 17:37:50</dateadded>
        <format>png</format>
                <sizes>
                    <size name="original" width="500" height="333">http://userserve-ak.last.fm/serve/_/54238609/Cur+de+Pirate+PNG.png</size>
                    <size name="large" width="126" height="84">http://userserve-ak.last.fm/serve/126/54238609.png</size>
                    <size name="largesquare" width="126" height="126">http://userserve-ak.last.fm/serve/126s/54238609.png</size>
                    <size name="medium" width="64" height="43">http://userserve-ak.last.fm/serve/64/54238609.png</size>
                    <size name="small" width="34" height="23">http://userserve-ak.last.fm/serve/34/54238609.png</size>
                    <size name="extralarge" width="252" height="168">http://userserve-ak.last.fm/serve/252/54238609.png</size>
                </sizes>
        <votes>
            <thumbsup>107</thumbsup>
            <thumbsdown>29</thumbsdown>
        </votes>
    </image>"""
TEST_MP3_IMAGE_URL = "http://userserve-ak.last.fm/serve/_/54238609/Cur+de+Pirate+PNG.png"
TEST_BINARY_DATA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABsAAAAXCAYAAAD6FjQuAAAExUlEQVRIS61WW2sdVRhd+zIz55KUeItIa6SY2BefREWFvNkq3lpaE1PB+ANEreJDi2/20UuLoi/+AK/FKAehtViKCqJQAtpGKkaQ+hQhaZJzmTmzZ7u+PXNS9OlEnMPhzJm951vf+i7r28o77xEu/miPPM+hbYQCCr1eH/VaVC7z4hIKX6AWaWRpF0kcA0oh7/dhbRL2ZFmBONHwNKuUR3tzHc2REa5oqC0wRWOugDYaBe8Hl3fBHmiPRoJLW5dsK8THap0+lm4XgNV8L/yhh3IpghV0gWvBSBbwaUBY0DgJQHGvtXzGNz3/y76wXhkUO/3qXtYEQL58BXkPaAhhWQi2CDYwIEaOv/k+arUdcART3iBRdWR9h5yfuGbRz9p00hOcEeB+YywK3nh6Y4xBmvYRE6lmHF55fg5CVoWN8lsxY3jRp0vHT36CXDfoiGfcDTdEvLPIaDEh1bpqo91Zh6mPEpDgztMOgZQJeXJ8ZnwfiW/j6EsHEZWlIFGk8xUzoZoR7LUTXyAzjZDcwNknZEAWwtI62N4KYoKmOkGHsbQmgtYWmqCOoI6gJdg6jh05CImiDsWihgOTvOhIId1cwZ6d12PP1G6YketQWFajjtBqtRCbmM4pRodgIFixiWMvPlWC8T+5DwtGr10bN44aPDvzMG4YA7o0wvxLKvD6yVOIyLAIYDGfZWRGsBcObx+MwaHnGW69qYm5J6ZDdTpm/mrK7wbw0cctFAypE04qYhgdwTbIbBbkTmaO3yGZycvIV3Hn5E4c3n8fwwWc/vYnLC4tw7CZ1zd7zAmrknnNCSbOlWBPlmBVLw5VIJLw0SjD5K4xPL73AdTrwIetb7D06xU0doxhba2DKKojD2AJwfIQxqNHDlQFUjb+UGCWYPOzDxLQYXxEsd80/uoAKxs5Vle7OP3VObLSBIv+D7CUXu5DjSGJcsZfmpeeiuKIGL319mdsEbJiXkpm/wrjdnJmfcqe2RfiX5Pmp5ZlFEJHwC7T+e57C1QQMqNeXMvZ1f9aIMxZ3MHEeB1PH9jLqQCc+e4ivr/wM5QdRS+TdpbSJyBLXykpfTY1C2TbTS0FYooNln4D8zMPIaGF1vmL+GHxF+YpZvIFoKzGraYOCjIokG0oSJmDDHfsHsehR+4KwrtwZhGXfvsTNmmi2+E8M0klV5QuZrPm1wi2PzAzIsTDaqOicGrfwdTEOGYfvRsRLXx+9jJ+XLwEE1OQmS8dhJhFL0KMNIC9KsxEhKUxWftDlb4wA1V88rabMfPYvewp4NMvL2Bp+QrVvAFH9RCFkOkuKiJgjUKYzQZmilFhcq+BCXgYMSdOIf+H6nMTzcQmx65bxjB3aDoM2IWzBLv8O48HDJNm3gZgnCWGqlkWyDOsYHFBmoR59eFcUA7CjIBvvPMBnOecKsgmDEcDzSSpPMXU7RO4f/oetpTG1+fOY3n5DzSiBic/Rz5nnuIgzWjJFRmaSY6Xn5uH5TnAhOkpZ5AKjANWpgW6dCJiQw3OGhxTsGQsY97JeYQyL6+GscNveM53RJw7/DXsfHlX7DVpT4anHEq0rsDkNXnWk83SucKyOntImCRHcugRfZMDjlRjLGNe8kEH5HkA4HOmJtzLWj91ZChqXz74G5pJ+8yqvUAdAAAAAElFTkSuQmCC"

def setCurrentUser(email, user_id, is_admin=False):
  os.environ['USER_EMAIL'] = email or ''
  os.environ['USER_ID'] = user_id or ''
  os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

def logoutCurrentUser():
  setCurrentUser(None, None)

class Tests(unittest.TestCase):
  def setUp(self):
    app_name = 'the-curator'
    os.environ['APPLICATION_ID'] = app_name
    datastore_file = '/dev/null'
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub(app_name, datastore_file, '/')
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
    apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', 
                                            urlfetch_stub.URLFetchServiceStub()) 
    self.testbed =  testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_urlfetch_stub()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_user_stub()
    self.testbed.init_images_stub()
      
  def testSetUp(self):
    self.testbed.deactivate()
  
  def test_decode_base64_image(self):
    image = images.Image(decode_base64_image(TEST_BINARY_DATA))
    self.assertEqual(image.width, 27)
    self.assertEqual(image.height, 23)
    self.assertEqual(image.format, images.PNG)

  def test_resize(self):
    image = decode_base64_image(TEST_BINARY_DATA)
    img = images.Image(resize(image))
    self.assertEqual(img.width, 200)
    self.assertEqual(int(img.height), 170)
    
  def test_get_image_type(self):
    self.assertEquals(get_image_type(TEST_BINARY_DATA), 'png')
    self.assertEquals(get_image_type(TEST_IMAGE_LINK), 'png')
    self.assertEquals(get_image_type('file.mp3'), None)
    self.assertEquals(get_image_type('data:image/gif'), 'gif')
  
  def test_get_image_from_xml(self):
    self.assertEquals(get_image_from_xml(TEST_MP3_IMAGE_XML), TEST_MP3_IMAGE_URL)
  
  def test_get_music_file(self):
    song, type = get_music_file(TEST_MP3, True)
    self.assertNotEquals(song.find(TEST_MP3_SONG_TITLE), -1)
    self.assertEquals(type, 'audio/mpeg')
  
  def test_get_cover_art(self):
    art = get_cover_art_link(TEST_MP3_SONG_TITLE, TEST_MP3_ARTIST)
    self.assertEquals(art, 'http://userserve-ak.last.fm/serve/_/45807281/David+Guetta+png.png')

  def test_add_music_logged_out(self):
    logoutCurrentUser()
    music = add_music(title=TEST_MP3_SONG_TITLE, artist=TEST_MP3_ARTIST, link=TEST_MP3)
    self.assertEquals(None, music)
 
  def test_add_music_no_problem(self):
    EMAIL = 'akiva@gmail.com'
    NAME = 'akiva'
    setCurrentUser(EMAIL, NAME)
    music = add_music(title=TEST_MP3_SONG_TITLE, artist=TEST_MP3_ARTIST, link=TEST_MP3)
    self.assertEquals(music.user.name, NAME)
    self.assertEquals(music.title, TEST_MP3_SONG_TITLE)
    self.assertEquals(music.artist, TEST_MP3_ARTIST)
    if music.data:
      self.assertEquals(music.data.link, TEST_MP3)
    self.assertEquals(music.image.link, get_cover_art_link(TEST_MP3_SONG_TITLE, TEST_MP3_ARTIST))
 
  def test_add_music_bad_link(self):
    EMAIL = 'akiva@gmail.com'
    NAME = 'akiva'
    setCurrentUser(EMAIL, NAME)
    LINK = 'nothing'
    music = add_music(title=TEST_MP3_SONG_TITLE, artist=TEST_MP3_ARTIST, link=LINK)
    self.assertEquals(music.user.name, NAME)
    self.assertEquals(music.title, TEST_MP3_SONG_TITLE)
    self.assertEquals(music.artist, TEST_MP3_ARTIST)
    self.assertEquals(music.data.hash, 'music_without_data')
    self.assertEquals(music.image.link, get_cover_art_link(TEST_MP3_SONG_TITLE, TEST_MP3_ARTIST))
    img = images.Image(music.image.data)
    self.assertEquals(img.width, 200)
    
  def test_add_image_logged_out(self):
    logoutCurrentUser()
    image = add_image(link=TEST_IMAGE_LINK)
    self.assertEquals(image, None)
  
  def test_add_image_with_link(self):
    EMAIL = 'akiva@gmail.com'
    NAME = 'akiva'
    setCurrentUser(EMAIL, NAME)
    image = add_image(link=TEST_IMAGE_LINK)
    self.assertEquals(image.user.name, NAME)
    self.assertEquals(image.artist, NAME)
    self.assertEquals(image.data.link, TEST_IMAGE_LINK)
    img = images.Image(image.data.data)
    self.assertEquals(img.width, 32)
    self.assertEquals(img.height, 32)
  
    
  def test_add_image_with_data(self):
    EMAIL = 'akiva@gmail.com'
    NAME = 'akiva'
    setCurrentUser(EMAIL, NAME)
    image = add_image(data=TEST_BINARY_DATA)
    self.assertEquals(image.user.name, NAME)
    self.assertEquals(image.artist, NAME)
    self.assertEquals(image.data.link, 'binary data')
    img = images.Image(image.data.data)
    self.assertEqual(img.width, 27)
    self.assertEqual(img.height, 23)
    self.assertEqual(img.format, images.PNG)
  
  def test_add_same_image_with_data(self):
    EMAIL = 'akiva@gmail.com'
    NAME = 'akiva'
    setCurrentUser(EMAIL, NAME)
    add_image(data=TEST_BINARY_DATA)
    EMAIL2 = 'test@gmail.com'
    NAME2 = 'test'
    setCurrentUser(EMAIL2, NAME2)
    image2 = add_image(data=TEST_BINARY_DATA)
    self.assertEquals(image2.artist, NAME)
    
      
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
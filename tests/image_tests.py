from nose.tools import *
import albatross
import datetime
import pytz

class testImageClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.validImage = self.etiConn.image(md5="5775a805d64965e396948f8c8aadd1e1", filename="image.png")
    self.gifImage = self.etiConn.image(md5="1dcc86742737b4356228e01505cf449b", filename="Waspinator9063.gif")
    self.jpgImage = self.etiConn.image(md5="8db4b31dca777fe09d4971f77d03f263", filename="spidersan.jpg")

  @raises(TypeError)
  def testNoMD5InvalidImage(self):
    self.etiConn.image(filename="doesnt-exist.png")

  @raises(albatross.InvalidImageError)
  def testInvalidMD5Image(self):
    self.etiConn.image(filename="doesnt-exist.png", md5="fakemd5").load()

  def testcheckImageValid(self):
    assert isinstance(self.validImage, albatross.Image)
    assert isinstance(self.gifImage, albatross.Image)

  def testgetImageMD5(self):
    assert isinstance(self.validImage.md5, unicode) and self.validImage.md5 == u"5775a805d64965e396948f8c8aadd1e1"
    assert isinstance(self.gifImage.md5, unicode) and self.gifImage.md5 == u"1dcc86742737b4356228e01505cf449b"
    assert isinstance(self.jpgImage.md5, unicode) and self.jpgImage.md5 == u"8db4b31dca777fe09d4971f77d03f263"

  def testgetImageFilename(self):
    assert isinstance(self.validImage.filename, unicode) and self.validImage.filename == u"image.png"
    assert isinstance(self.gifImage.filename, unicode) and self.gifImage.filename == u"Waspinator9063.gif"
    assert isinstance(self.jpgImage.filename, unicode) and self.jpgImage.filename == u"spidersan.jpg"

  def testgetImageRelatedImages(self):
    assert isinstance(self.validImage.relatedImages, list) and isinstance(self.validImage.relatedImages[0], albatross.Image)
    assert isinstance(self.gifImage.relatedImages, list) and isinstance(self.gifImage.relatedImages[0], albatross.Image)
    assert isinstance(self.jpgImage.relatedImages, list) and isinstance(self.jpgImage.relatedImages[0], albatross.Image)

  def testgetImageTopics(self):
    assert isinstance(self.validImage.topics, list) and isinstance(self.validImage.topics[0], albatross.Topic)
    assert isinstance(self.gifImage.topics, list) and isinstance(self.gifImage.topics[0], albatross.Topic)
    assert isinstance(self.jpgImage.topics, list) and isinstance(self.jpgImage.topics[0], albatross.Topic)
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
    self.neverPostedImage = self.etiConn.image(md5="6c5039d92445cd1c0e9a9c18428bcbc3", filename="eti-blank-neverpost.png")

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
    assert isinstance(self.validImage.related, list) and isinstance(self.validImage.related[0], albatross.Image)
    assert isinstance(self.gifImage.related, list) and isinstance(self.gifImage.related[0], albatross.Image)
    assert isinstance(self.jpgImage.related, list) and isinstance(self.jpgImage.related[0], albatross.Image)

  def testgetImageRelatedImageCount(self):
    assert isinstance(self.validImage.relatedCount, int) and self.validImage.relatedCount > 0
    assert isinstance(self.neverPostedImage.relatedCount, int) and self.neverPostedImage.relatedCount == 0

  def testgetImageTopics(self):
    assert isinstance(self.validImage.topics, list) and isinstance(self.validImage.topics[0], albatross.Topic)
    assert isinstance(self.gifImage.topics, list) and isinstance(self.gifImage.topics[0], albatross.Topic)
    assert isinstance(self.jpgImage.topics, list) and isinstance(self.jpgImage.topics[0], albatross.Topic)

  def testgetImageTopicCount(self):
    assert isinstance(self.validImage.topicCount, int) and self.validImage.topicCount > 0
    assert isinstance(self.neverPostedImage.topicCount, int) and self.neverPostedImage.topicCount == 0


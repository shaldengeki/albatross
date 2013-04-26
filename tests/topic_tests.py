from nose.tools import *
import albatross
import datetime
import pytz

class testTopicClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    klass.centralTimezone = pytz.timezone('America/Chicago')

    klass.validTopic = klass.etiConn.topics.search(allowedTags=["LUE"])[0]
    klass.archivedTopic = klass.etiConn.topic(6240806)
    klass.multiPageTopic = klass.etiConn.topic(6240806, page=2)
    klass.lastPageTopic = klass.etiConn.topic(6240806, page=3)
    klass.starcraftTopic = klass.etiConn.topic(6951014)
    klass.anonymousTopic = klass.etiConn.topic(8431797)

  @raises(TypeError)
  def testNoIDInvalidTopic(self):
    self.etiConn.topic()

  @raises(albatross.InvalidTopicError)
  def testNegativeInvalidTopic(self):
    self.etiConn.topic(-1)

  @raises(albatross.InvalidTopicError)
  def testBoolInvalidTopic(self):
    self.etiConn.topic(False)

  @raises(albatross.InvalidTopicError)
  def testFloatInvalidTopic(self):
    self.etiConn.topic(1.5)

  def testcheckTopicValid(self):
    assert isinstance(self.validTopic, albatross.Topic)

  def testcheckArchivedTopic(self):
    assert isinstance(self.archivedTopic.archived, bool) and self.archivedTopic.archived
    assert isinstance(self.validTopic.archived, bool) and not self.validTopic.archived
  
  def testgetTopicID(self):
    assert self.archivedTopic.id == 6240806
    assert self.multiPageTopic.id == 6240806
    assert self.lastPageTopic.id == 6240806
    assert self.starcraftTopic.id == 6951014
    
  def testgetTopicTitle(self):
    assert isinstance(self.starcraftTopic.title, str) and self.starcraftTopic.title

  def testgetTopicDate(self):
    assert self.starcraftTopic.date and isinstance(self.starcraftTopic.date, datetime.datetime) and self.starcraftTopic.date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)

  def testgetTopicPageNum(self):
    assert self.starcraftTopic.page == 1
    assert self.multiPageTopic.page == 2
    assert self.lastPageTopic.page == 3

  def testgetTopicNumPages(self):
    assert self.starcraftTopic.pages == 1
    assert self.multiPageTopic.pages == 3
    assert self.lastPageTopic.pages == 3

  def testgetTopicPosts(self):
    assert isinstance(self.validTopic.posts(), list) and self.validTopic.posts()
    assert isinstance(self.starcraftTopic.posts(), list) and self.starcraftTopic.posts() and len(self.starcraftTopic.posts()) == 2
    assert isinstance(self.archivedTopic.posts(), list) and self.archivedTopic.posts() and len(self.archivedTopic.posts()) == 106

  def testgetTopicTags(self):
    assert isinstance(self.validTopic.tags, albatross.TagList) and "LUE" in self.validTopic.tags._tagNames
    assert isinstance(self.starcraftTopic.tags, albatross.TagList) and len(self.starcraftTopic.tags) == 3 and "Archived" in self.starcraftTopic.tags._tagNames and "Starcraft" in self.starcraftTopic.tags._tagNames and "LUE" in self.starcraftTopic.tags._tagNames

  def testgetTopicUser(self):
    assert self.anonymousTopic.user['id'] == 0 and self.anonymousTopic.user['name'] == 'Human'
    assert self.starcraftTopic.user['id'] == 4662 and self.starcraftTopic.user['name'] == 'tsutter810'
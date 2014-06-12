from nose.tools import *
import albatross
import datetime
import pytz

class testTopicClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.centralTimezone = pytz.timezone('America/Chicago')

    self.validTopic = self.etiConn.topics(allowedTags=["LUE"]).search()[0]
    self.archivedTopic = self.etiConn.topic(6240806)
    self.falseArchivedTopic = self.etiConn.topic(6240806).set({'archived': False})
    self.multiPageTopic = self.etiConn.topic(6240806, page=2)
    self.lastPageTopic = self.etiConn.topic(6240806, page=3)
    self.starcraftTopic = self.etiConn.topic(6951014)
    self.anonymousTopic = self.etiConn.topic(8431797)

    self.lueTag = self.etiConn.tag("LUE")
    self.archivedTag = self.etiConn.tag("Archived")
    self.starcraftTag = self.etiConn.tag("Starcraft")

  @raises(TypeError)
  def testNoIDInvalidTopic(self):
    self.etiConn.topic()

  @raises(albatross.InvalidTopicError)
  def testNegativeInvalidTopic(self):
    self.etiConn.topic(-1)

  @raises(albatross.InvalidTopicError)
  def testFloatInvalidTopic(self):
    self.etiConn.topic(1.5)

  def testTopicLength(self):
    assert len(self.archivedTopic) == 106
    assert len(self.starcraftTopic) == 2
    assert len(self.validTopic) > 0

  def testcheckTopicValid(self):
    assert isinstance(self.validTopic, albatross.Topic)

  def testcheckArchivedTopic(self):
    assert isinstance(self.archivedTopic.archived, bool)
    assert self.archivedTopic.archived
    assert isinstance(self.validTopic.archived, bool)
    assert not self.validTopic.archived

  def testcheckClosedTopic(self):
    assert isinstance(self.archivedTopic.closed, bool)
    assert self.archivedTopic.closed
    assert isinstance(self.validTopic.closed, bool)
    assert not self.validTopic.closed
  
  @raises(albatross.ArchivedTopicError)
  def testCheckInvalidArchivedStatus(self):
    self.falseArchivedTopic.load()

  @raises(albatross.PageLoadError)
  def testFetchMalformedTopic(self):
    self.archivedTopic.appendPosts(None, None, None, None)

  def testgetTopicID(self):
    assert self.archivedTopic.id == 6240806
    assert self.multiPageTopic.id == 6240806
    assert self.lastPageTopic.id == 6240806
    assert self.starcraftTopic.id == 6951014
    
  def testgetTopicTitle(self):
    assert isinstance(self.starcraftTopic.title, unicode)
    assert self.starcraftTopic.title

  def testgetTopicDate(self):
    assert self.starcraftTopic.date
    assert isinstance(self.starcraftTopic.date, datetime.datetime)
    assert self.starcraftTopic.date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)

  def testgetTopicLastPostTime(self):
    assert self.starcraftTopic.lastPostTime
    assert isinstance(self.starcraftTopic.lastPostTime, datetime.datetime)
    assert self.starcraftTopic.lastPostTime == datetime.datetime.fromtimestamp(1296774689, tz=self.centralTimezone)

  def testgetTopicPageNum(self):
    assert self.starcraftTopic.page == 1
    assert self.multiPageTopic.page == 2
    assert self.lastPageTopic.page == 3

  def testgetTopicNumPages(self):
    assert self.starcraftTopic.pages == 1
    assert self.multiPageTopic.pages == 3
    assert self.lastPageTopic.pages == 3

  def testgetTopicPosts(self):
    assert isinstance(self.validTopic.posts()[0], albatross.Post)
    assert isinstance(self.starcraftTopic.posts()[0], albatross.Post)
    assert isinstance(self.archivedTopic.posts()[0], albatross.Post)

  def testgetPostCount(self):
    assert isinstance(self.validTopic.postCount, int)
    assert self.validTopic.postCount > 0
    assert isinstance(self.starcraftTopic.postCount, int)
    assert self.starcraftTopic.postCount == 2
    assert isinstance(self.archivedTopic.postCount, int)
    assert self.archivedTopic.postCount
    assert self.archivedTopic.postCount == 106

  def testgetTopicTags(self):
    assert isinstance(self.validTopic.tags, albatross.TagList)
    assert self.lueTag in self.validTopic.tags
    assert isinstance(self.starcraftTopic.tags, albatross.TagList)
    assert len(self.starcraftTopic.tags) == 3
    assert self.archivedTag in self.starcraftTopic.tags
    assert self.starcraftTag in self.starcraftTopic.tags
    assert self.lueTag in self.starcraftTopic.tags

  def testgetTopicUser(self):
    assert self.anonymousTopic.user.id == 0
    assert self.anonymousTopic.user.name == 'Human'
    assert self.starcraftTopic.user.id == 4662
    assert self.starcraftTopic.user.name == 'tsutter810'
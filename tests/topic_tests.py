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

    klass.validTopicID = klass.etiConn.topics.search(allowedTags=["LUE"])[0].id

    klass.validTopic = klass.etiConn.topic(klass.validTopicID)
    klass.archivedTopic = klass.etiConn.topic(6240806)
    klass.invalidTopic = klass.etiConn.topic(0)
    klass.multiPageTopic = klass.etiConn.topic(6240806, page=2)
    klass.lastPageTopic = klass.etiConn.topic(6240806, page=3)
    klass.starcraftTopic = klass.etiConn.topic(6951014)

  def testcheckTopicValid(self):
    assert isinstance(self.validTopic, albatross.Topic)

  @raises(albatross.InvalidTopicException)
  def testcheckTopicInvalid(self):
    self.invalidTopic.load()
    
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

  @raises(albatross.InvalidTopicException)
  def testgetInvalidTopicTitle(self):
    self.invalidTopic.title

  def testgetTopicDate(self):
    assert self.starcraftTopic.date and isinstance(self.starcraftTopic.date, datetime.datetime) and self.starcraftTopic.date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)

  @raises(albatross.InvalidTopicException)
  def testinvalidTopicDate(self):
    self.invalidTopic.date

  def testgetTopicPageNum(self):
    assert self.starcraftTopic.page == 1
    assert self.multiPageTopic.page == 2
    assert self.lastPageTopic.page == 3

  def testgetTopicNumPages(self):
    assert self.starcraftTopic.pages == 1
    assert self.multiPageTopic.pages == 3
    assert self.lastPageTopic.pages == 3

  @raises(albatross.InvalidTopicException)
  def testgetInvalidTopicPosts(self):
    self.invalidTopic.posts

  def testgetTopicPosts(self):
    assert isinstance(self.validTopic.posts, list) and self.validTopic.posts
    assert isinstance(self.starcraftTopic.posts, list) and self.starcraftTopic.posts and len(self.starcraftTopic.posts) == 2
    assert isinstance(self.archivedTopic.posts, list) and self.archivedTopic.posts and len(self.archivedTopic.posts) == 106
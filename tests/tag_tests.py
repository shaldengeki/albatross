from nose.tools import *
import albatross

class testTagClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.invalidTag = self.etiConn.tag("paoisjdfpoasijdfpoasidjfpaosijf")
    self.lueTag = self.etiConn.tag("LUE")
    self.tvTag = self.etiConn.tag("TV")
    self.gleeTag = self.etiConn.tag("Glee")
    self.threeTags = self.etiConn.tags(tags=["TV", "LUE", "Glee"])

  def testgetTagInfo(self):
    assert isinstance(self.lueTag, albatross.Tag)
    assert self.lueTag.name == "LUE"
    assert len(self.lueTag.description) > 0

    assert isinstance(self.tvTag, albatross.Tag)
    assert self.tvTag.name == "TV"
    assert len(self.tvTag.description) > 0

    assert isinstance(self.threeTags, albatross.TagList)
    assert len(self.threeTags) == 3
    assert self.threeTags[0].name != ''

  def testgetTagStaff(self):
    assert isinstance(self.lueTag.staff, list)
    assert len(self.lueTag.staff) > 0

    assert isinstance(self.lueTag.staff[0]['user'], albatross.User)
    assert isinstance(self.lueTag.staff[0]['user'].id, int)
    assert isinstance(self.lueTag.staff[0]['user'].name, unicode)
    assert self.lueTag.staff[0]['role'] in ('administrator', 'moderator')

  def testtagRelatedTags(self):
    assert len(self.tvTag.related) > 0
    assert isinstance(self.tvTag.related[0], albatross.Tag)
    assert self.tvTag.related[0].name

    assert len(self.tvTag.dependent) > 0
    assert isinstance(self.tvTag.dependent[0], albatross.Tag)
    assert self.tvTag.dependent[0].name

    assert len(self.tvTag.forbidden) > 0
    assert isinstance(self.tvTag.forbidden[0], albatross.Tag)
    assert self.tvTag.forbidden[0].name

  @raises(albatross.InvalidTagError)
  def testgetInvalidTagInfo(self):
    self.invalidTag.description

  @raises(albatross.MalformedTagError)
  def testParseInvalidJSON(self):
    self.lueTag.parse("THIS IS INVALID JSON")

  def testgetTagTopics(self):
    assert isinstance(self.tvTag.topics().search(), albatross.TopicList)
    assert len(self.tvTag.topics().search()) > 0
    assert all([self.tvTag in topic.tags for topic in self.tvTag.topics().search()])
    assert isinstance(self.threeTags.topics().search(), albatross.TopicList)
    assert len(self.threeTags.topics().search()) > 0
    assert all([self.tvTag in topic.tags or self.lueTag in topic.tags or self.gleeTag in topic.tags for topic in self.threeTags.topics().search()])
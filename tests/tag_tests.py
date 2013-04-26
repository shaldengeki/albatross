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
    self.threeTags = self.etiConn.tags(tags=["TV", "LUE", "Glee"])

  def testgetTagInfo(self):
    assert isinstance(self.lueTag, albatross.Tag) and self.lueTag.name == "LUE" and len(self.lueTag.description) > 0
    assert isinstance(self.tvTag, albatross.Tag) and self.tvTag.name == "TV"  and len(self.tvTag.description) > 0
    assert isinstance(self.threeTags, albatross.TagList) and len(self.threeTags) == 3 and self.threeTags[0].name != ''

  def testgetTagStaff(self):
    assert isinstance(self.lueTag.staff, list) and len(self.lueTag.staff) > 0 and isinstance(self.lueTag.staff[0], dict) and isinstance(self.lueTag.staff[0]['id'], int) and (isinstance(self.lueTag.staff[0]['name'], str) or isinstance(self.lueTag.staff[0]['name'], unicode)) and self.lueTag.staff[0]['role'] in ('administrator', 'moderator')

  def testtagRelatedTags(self):
    assert len(self.tvTag.related) > 0 and isinstance(self.tvTag.related[0], albatross.Tag) and self.tvTag.related[0].name
    assert len(self.tvTag.dependent) > 0 and isinstance(self.tvTag.dependent[0], albatross.Tag) and self.tvTag.dependent[0].name
    assert len(self.tvTag.forbidden) > 0 and isinstance(self.tvTag.forbidden[0], albatross.Tag) and self.tvTag.forbidden[0].name

  @raises(albatross.InvalidTagError)
  def testgetInvalidTagInfo(self):
    self.invalidTag.description
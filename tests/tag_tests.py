from nose.tools import *
import albatross

class testTagClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    klass.invalidTag = klass.etiConn.tag("paoisjdfpoasijdfpoasidjfpaosijf")
    klass.lueTag = klass.etiConn.tag("LUE")
    klass.tvTag = klass.etiConn.tag("TV")
    klass.threeTags = klass.etiConn.tags(tags=["TV", "LUE", "Glee"])

  def testgetTagInfo(self):
    assert isinstance(self.lueTag, albatross.Tag) and self.lueTag.name == "LUE" and len(self.lueTag.staff) > 0 and len(self.lueTag.description) > 0
    assert isinstance(self.tvTag, albatross.Tag) and self.tvTag.name == "TV" and len(self.tvTag.staff) > 0 and len(self.tvTag.description) > 0 and len(self.tvTag.related) > 0
    assert isinstance(self.threeTags, albatross.TagList) and len(self.threeTags) == 3 and self.threeTags[0].name != ''

  def testtagRelatedTags(self):
    assert len(self.tvTag.related) > 0 and isinstance(self.tvTag.related[0], albatross.Tag) and self.tvTag.related[0].name
    assert len(self.tvTag.dependent) > 0 and isinstance(self.tvTag.dependent[0], albatross.Tag) and self.tvTag.dependent[0].name
    assert len(self.tvTag.forbidden) > 0 and isinstance(self.tvTag.forbidden[0], albatross.Tag) and self.tvTag.forbidden[0].name

  @raises(albatross.InvalidTagException)
  def testgetInvalidTagInfo(self):
    self.invalidTag.description
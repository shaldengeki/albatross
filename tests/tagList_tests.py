from nose.tools import *
import albatross

class testTagListClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.activeTagList = self.etiConn.tags(active=True)
    self.emptyTagList = self.etiConn.tags(tags=[])
    self.tagList = self.etiConn.tags(tags=["LUE", "TV", "Anime"])

  def testgetActiveTags(self):
    assert isinstance(self.activeTagList, albatross.TagList) and len(self.activeTagList) > 0
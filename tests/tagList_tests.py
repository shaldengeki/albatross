from nose.tools import *
import albatross

class testTagListClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    klass.activeTagList = klass.etiConn.tags(active=True)

  def testgetActiveTags(self):
    assert isinstance(self.activeTagList, albatross.TagList) and len(self.activeTagList) > 0
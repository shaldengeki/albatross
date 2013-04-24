from nose.tools import *
import albatross

class testPageClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    # main page HTML for getEnclosedString test.
    klass.mainPageText = klass.etiConn.page('https://endoftheinter.net/main.php').html
    
    # klass.validTopicID = klass.etiConn.topics.search(allowedTags=["LUE"])[0].id
    # klass.validTopic = klass.etiConn.topic(klass.validTopicID)
    # klass.archivedRedirectTopic = klass.etiConn.topic(6240806)
    # klass.validTopicHeader = klass.etiConn.page(klass.etiConn.topic(klass.validTopicID).page(1).url).header
    # klass.archivedRedirectText = klass.etiConn.page(klass.etiConn.topic(6240806).page(1).url).header

  def testgetEnclosedString(self):
    assert not albatross.getEnclosedString(self.mainPageText, 'aspdfasdpofijas', 'aspdfasdpofijas')
    assert albatross.getEnclosedString(self.mainPageText, '<h1>', '</h1>') == 'End of the Internet'    
    assert not albatross.getEnclosedString("", "<h1>", "</h1>")
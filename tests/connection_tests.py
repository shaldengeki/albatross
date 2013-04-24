from nose.tools import *
import albatross

class testConnectionClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.connection.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

  def testcheckETIUp(self):
    ''' there is no good way to test this ugh '''
    assert self.etiConn.etiUp()

  def testlogin(self):
    (tempUsername, tempPassword) = (self.etiConn.username,self.etiConn.password)
    (self.etiConn.username, self.etiConn.password) = ("FAKE USERNAME", "FAKE PASSWORD")
    assert not self.etiConn.login()
    (self.etiConn.username, self.etiConn.password) = (tempUsername, tempPassword)
    assert self.etiConn.login()

  def testloggedIn(self):
    tempCookieString = self.etiConn.cookieString
    self.etiConn.cookieString = "FAKE COOKIESTRING"
    assert not self.etiConn.loggedIn()
    self.etiConn.cookieString = tempCookieString
    assert self.etiConn.loggedIn()

  def testpage(self):
    assert isinstance(self.etiConn.page('https://endoftheinter.net'), albatross.Page)

  def testtopics(self):
    assert isinstance(self.etiConn.topics, albatross.TopicList)
from nose.tools import *
import albatross

class testConnectionClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, cookieFile='cookieString.txt', loginSite=albatross.SITE_MOBILE)
    self.exampleCookieHeader = """HTTP/1.1 302 Moved Temporarily\r\nServer: nginx/1.2.1\r\nDate: Fri, 26 Apr 2013 07:54:13 GMT\r\nContent-Type: text/html\r\nTransfer-Encoding: chunked\r\n\Connection: keep-alive\r\nKeep-Alive: timeout=70\r\nExpires: Thu, 19 Nov 1981 08:52:00 GMT\r\nCache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0\r\nPragma: no-cache\r\nSet-Cookie: userid=12345; expires=Sat, 26-Apr-2014 07:54:13 GMT; path=/; domain=.endoftheinter.net\r\nSet-Cookie: session=2byudk3fs8da098gpqbhn2jh2oiuhasd; expires=Sat, 26-Apr-2014 07:54:13 GMT; path=/; domain=.endoftheinter.net\r\nLocation: http://endoftheinter.net/main.php\r\nContent-Encoding: gzip\r\nVary: Accept-Encoding"""

  def testParseCookieHeader(self):
    assert self.etiConn.parseCookieHeader(self.exampleCookieHeader) == "userid=12345; session=2byudk3fs8da098gpqbhn2jh2oiuhasd"

  @raises(albatross.UnauthorizedError)
  def testGetInvalidPage(self):
    invalidConn = albatross.Connection(username="Albatross Test", password="Testing Albatross", loginSite=albatross.SITE_MOBILE)
    invalidConn.topic(1).posts()

  def testCookieStringCookieFileLogin(self):
    with open('cookieString.txt', 'w') as cookieFile:
      cookieFile.write(self.etiConn.cookieString)
      self.cookieStringLogin = albatross.Connection(cookieString=self.etiConn.cookieString, cookieFile='cookieString.txt')
      assert self.cookieStringLogin.loggedIn()

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
    (oldCookieString, self.etiConn.cookieString) = (self.etiConn.cookieString, 'FAKE COOKIESTRING')
    assert not self.etiConn.loggedIn()
    self.etiConn.cookieString = oldCookieString
    assert self.etiConn.loggedIn()

  def testreauthenticate(self):
    self.etiConn.cookieString = 'FAKE COOKIESTRING'
    assert not self.etiConn.loggedIn()
    assert self.etiConn.reauthenticate()
    assert self.etiConn.loggedIn()
    with open('cookieString.txt', 'r') as cookieFile:
      assert unicode(cookieFile.read().strip()) == self.etiConn.cookieString

  def testpage(self):
    assert isinstance(self.etiConn.page('https://endoftheinter.net'), albatross.Page)

  def testtopics(self):
    assert isinstance(self.etiConn.topics(), albatross.TopicList)

  def testtopic(self):
    assert isinstance(self.etiConn.topic(1), albatross.Topic)

  def testtags(self):
    assert isinstance(self.etiConn.tags(), albatross.TagList)
    # assert isinstance(self.etiConn.tags(active=True), albatross.TagList) and len(self.etiConn.tags(active=True)) > 0

  def testtag(self):
    assert isinstance(self.etiConn.tag('LUE'), albatross.Tag)

  def testimage(self):
    assert isinstance(self.etiConn.image(md5='5775a805d64965e396948f8c8aadd1e1', filename='image.png'), albatross.Image)

  def testpost(self):
    topic = self.etiConn.topic(1)
    assert isinstance(self.etiConn.post(1, topic), albatross.Post)

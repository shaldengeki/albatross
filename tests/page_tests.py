from nose.tools import *
import albatross

class testPageClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)
    self.fakeConn = albatross.Connection(username="a", password="b", loginSite=albatross.SITE_MOBILE)

    self.mainPage = self.etiConn.page('https://endoftheinter.net/main.php')
    self.doesntNeedAuthPage = self.fakeConn.page('https://endoftheinter.net/index.php')
    self.unauthedPage = self.fakeConn.page('https://endoftheinter.net/index.php', authed=False)
    self.needsAuthPage = self.fakeConn.page('https://endoftheinter.net/main.php')

  def testauthed(self):
    assert self.mainPage.authed == True
    assert self.unauthedPage.authed == False

  @raises(albatross.UnauthorizedError)
  def testAuthedPageWithUnauthedConn(self):
    self.needsAuthPage.html

  @raises(albatross.UnauthorizedError)
  def testUnauthedPageWithAuthedConn(self):
    self.doesntNeedAuthPage.html

  @raises(albatross.PageLoadError)
  def testGetInvalidPage(self):
    self.etiConn.page('https://endoftheinter.net/DOESNT_EXIST_FOO').html

  def testhtml(self):
    assert isinstance(self.mainPage.html, unicode) and "Das Ende des Internets" not in self.mainPage.html
    assert isinstance(self.unauthedPage.html, unicode) and "Das Ende des Internets" in self.unauthedPage.html

  def testheader(self):
    assert isinstance(self.mainPage.header, unicode) and len(self.mainPage.header) > 0
    assert isinstance(self.unauthedPage.header, unicode) and len(self.unauthedPage.header) > 0

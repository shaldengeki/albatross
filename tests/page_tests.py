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

    self.mainPage = self.etiConn.page('https://endoftheinter.net/main.php')

  @raises(albatross.UnauthorizedError)
  def testInvalidLogin(self):
    albatross.Connection(username="a", password="b", loginSite=albatross.SITE_MOBILE)

  def testauthed(self):
    assert self.mainPage.authed == True

  @raises(albatross.PageLoadError)
  def testGetInvalidPage(self):
    self.etiConn.page('https://endoftheinter.net/DOESNT_EXIST_FOO').html

  def testhtml(self):
    assert isinstance(self.mainPage.html, unicode) and "Das Ende des Internets" not in self.mainPage.html

  def testheader(self):
    assert isinstance(self.mainPage.header, unicode) and len(self.mainPage.header) > 0

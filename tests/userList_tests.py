from nose.tools import *
import albatross
import datetime
import pytz

class testUserListClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    # topic page and content HTML for topic tests.
    self.currentUserSearchPage = self.etiConn.page('https://endoftheinter.net/userlist.php')
    self.singleUserSearchPage = self.etiConn.page('https://endoftheinter.net/userlist.php?user=shaldengeki')
    self.multipleUserSearchPage = self.etiConn.page('https://endoftheinter.net/userlist.php?user=enk')
    self.emptyUserSearchPage = self.etiConn.page('https://endoftheinter.net/userlist.php?user=adsifasidfjapdsoifjapsodjf')

    self.currentUserSearch = self.etiConn.users().search()
    self.singleUserSearch = self.etiConn.users().search("shaldengeki")
    self.multiplePageSearch = self.etiConn.users().search("guy", recurse=True)
    self.emptyUserSearch = self.etiConn.users().search("adsifasidfjapdsoifjapsodjf")

    self.llamaGuy = self.etiConn.user(1)
    self.shaldengeki = self.etiConn.user(6731)

  def testgetTopicInfoFromListing(self):
    assert isinstance(self.currentUserSearch.parse(self.currentUserSearchPage.html), dict)
    assert len(self.currentUserSearch.parse(self.currentUserSearchPage.html)) > 0

  @raises(albatross.UserListError)
  def testgetTopicInfoFromEmptyListing(self):
    self.emptyUserSearch.parse(self.emptyUserSearchPage)

  @raises(IndexError)
  def testgetTopicInfoFromEmptyListing(self):
    self.emptyUserSearch[0]

  def testsearchUsers(self):
    assert isinstance(self.emptyUserSearch, albatross.UserList)
    assert len(self.emptyUserSearch) == 0

    assert isinstance(self.currentUserSearch, albatross.UserList)
    assert len(self.currentUserSearch) > 0

    assert isinstance(self.multiplePageSearch, albatross.UserList)
    assert len(self.multiplePageSearch) > 50

    assert isinstance(self.currentUserSearch[0], albatross.User)

    assert self.llamaGuy in self.currentUserSearch

    assert isinstance(self.singleUserSearch, albatross.UserList)
    assert len(self.singleUserSearch) == 1

    assert self.shaldengeki in self.singleUserSearch
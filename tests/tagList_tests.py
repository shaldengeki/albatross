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

    self.lueTag = self.etiConn.tag("LUE")
    self.tvTag = self.etiConn.tag("TV")
    self.animeTag = self.etiConn.tag("Anime")

    self.lueTagPage = self.etiConn.page('https://boards.endoftheinter.net/async-tag-query.php?e&q=LUE')

  def testappendFromTagPage(self):
    self.emptyTagList = self.etiConn.tags(tags=[])
    assert self.lueTag not in self.emptyTagList
    self.emptyTagList.appendFromTagPage(self.lueTagPage.html, self.lueTagPage.url, None, None)
    assert self.lueTag in self.emptyTagList
    self.emptyTagList = self.etiConn.tags(tags=[])

  def testgetActiveTags(self):
    assert isinstance(self.activeTagList, albatross.TagList) and len(self.activeTagList) > 0

  def testContainsTags(self):
    assert self.lueTag in self.tagList and self.tvTag in self.tagList and self.animeTag in self.tagList
    assert self.lueTag not in self.emptyTagList and self.tvTag not in self.emptyTagList and self.animeTag not in self.emptyTagList

  def testListLength(self):
    assert len(self.tagList) == 3
    assert len(self.emptyTagList) == 0
    assert len(self.activeTagList) > 0
from nose.tools import *
import albatross

class testAlbatrossClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    # cookieString = open('cookieFile.txt', 'r').readlines()[0].strip()
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Albatross(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)
    
    # main page HTML for getEnclosedString test.
    klass.mainPageText = klass.etiConn.getPage(url='https://endoftheinter.net/main.php')

    # link page HTML for link tests.
    # klass.firstLinkText = klass.etiConn.getLinkPage(18)
    # klass.secondLinkText = klass.etiConn.getLinkPage(389813)
    # klass.noLinkLinkText = klass.etiConn.getLinkPage(239465)
    # klass.deletedLinkText = klass.etiConn.getLinkPage(362550)
    # klass.invalidLinkText = klass.etiConn.getLinkPage(-1)
    
    # topic page and content HTML for topic tests.
    klass.currentTopicListPage = klass.etiConn.getPage(url = 'http://boards.clouds.endoftheinter.net/topics/')

    klass.validTopicID = klass.etiConn.getLatestTopicID(klass.currentTopicListPage)
    klass.validTopicText = klass.etiConn.getTopicPage(klass.validTopicID)
    klass.archivedTopicText = klass.etiConn.getTopicPage(6240806, archived=True)
    klass.archivedRedirectText = klass.etiConn.getTopicPage(6240806)
    klass.invalidTopicText = klass.etiConn.getTopicPage(0)
    klass.multiPageTopicText = klass.etiConn.getTopicPage(6240806, pageNum=2, archived=True)
    klass.lastPageTopicText = klass.etiConn.getTopicPage(6240806, pageNum=3, archived=True)
    klass.starcraftTopicText = klass.etiConn.getTopicPage(6951014, archived=True)
    
    klass.nwsTopicSearchList = klass.etiConn.getPage(url = 'http://boards.clouds.endoftheinter.net/topics/NWS')
    klass.emptyTopicSearchList = klass.etiConn.getPage(url = 'http://boards.clouds.endoftheinter.net/topics/?q=abiejgapsodijf')

    klass.nwsTopicSearch = klass.etiConn.searchTopics(query="NWS", topics=[], recurse=False)
    klass.archivesTopicSearch = klass.etiConn.searchTopics(query="Archived", topics=[], recurse=False)
    klass.emptyTopicSearch = klass.etiConn.searchTopics(query="abiejgapsodijf", topics=[])

    klass.emptyTopicList = klass.etiConn.getTopicList(maxTopicTime=1, maxTopicID=1, topics=[], recurse=False)
    klass.currentTopicList = klass.etiConn.getTopicList(topics=[], recurse=False)
    # klass.archivedTopicList = klass.etiConn.getTopicList(archived=True, boardID=42, pageNum=1, topics=[], recurse=True)
    
  def testLogin(self):
    assert not self.etiConn.login("FAKE USERNAME", "FAKE PASSWORD")
    assert self.etiConn.login(self.username, self.password)

  def testcheckLoggedIn(self):
    tempCookieString = self.etiConn.cookieString
    self.etiConn.cookieString = "FAKE COOKIESTRING"
    assert not self.etiConn.checkLoggedIn()
    self.etiConn.cookieString = tempCookieString
    assert self.etiConn.checkLoggedIn()
    
  def testgetEnclosedString(self):
    assert not self.etiConn.getEnclosedString(self.mainPageText, 'aspdfasdpofijas', 'aspdfasdpofijas')
    assert self.etiConn.getEnclosedString(self.mainPageText, '<h1>', '</h1>') == 'End of the Internet'    
    assert not self.etiConn.getEnclosedString("", "<h1>", "</h1>")
  # fuck llamaguy
  # def testgetLinkTitle(self):
    # assert albatross.getLinkTitle(self.firstLinkText) == 'I believe you have my stapler'
    # assert albatross.getLinkTitle(self.noLinkLinkText) == 'K-ON! (COMPLETE with albums)'
    # assert albatross.getLinkTitle(self.deletedLinkText) == 'Nodame Cantabile (HD)'
  
  # def testgetLinkLink(self):
    # assert albatross.getLinkLink(self.firstLinkText) == 'http://stapler.ytmnd.com/'
    # assert not albatross.getLinkLink(self.noLinkLinkText)
    # assert not albatross.getLinkLink(self.deletedLinkText)
  
  # def testgetLinkCreator(self):
    # assert albatross.getLinkCreator(self.firstLinkText) == dict([('userid', '1'), ('username', 'LlamaGuy')])
    # assert not albatross.getLinkCreator(self.deletedLinkText)
  
  # def testgetLinkDate(self):
    # assert not albatross.getLinkDate(self.firstLinkText)
    # assert albatross.getLinkDate(self.secondLinkText) == '8/23/2011 10:40:27 AM'
    # assert not albatross.getLinkDate(self.deletedLinkText)
  
  # def testgetLinkDateUnix(self):
    # assert not albatross.getLinkDateUnix(self.firstLinkText)
    # assert isinstance(albatross.getLinkDateUnix(self.secondLinkText), int) and albatross.getLinkDateUnix(self.secondLinkText) == 1314114027
  
  # def testgetLinkCode(self):
    # assert albatross.getLinkCode(self.firstLinkText) == 'LL12'
    # assert not albatross.getLinkDate(self.deletedLinkText)
  
  # def testgetLinkHits(self):
    # assert isinstance(albatross.getLinkHits(self.firstLinkText), int) and albatross.getLinkHits(self.firstLinkText) >= 0
    # assert not albatross.getLinkHits(self.deletedLinkText)
  
  # def testgetLinkRating(self):
    # assert isinstance(albatross.getLinkRating(self.firstLinkText), float) and albatross.getLinkRating(self.firstLinkText) >= 0
    # assert not albatross.getLinkRating(self.deletedLinkText)
  
  # def testgetLinkVotes(self):
    # assert isinstance(albatross.getLinkVotes(self.firstLinkText), int) and albatross.getLinkVotes(self.firstLinkText) >= 0
    # assert not albatross.getLinkVotes(self.deletedLinkText)

  # def testgetLinkRank(self):
    # assert isinstance(albatross.getLinkRank(self.firstLinkText), int) and albatross.getLinkRank(self.firstLinkText) >= 0
    # assert not albatross.getLinkRank(self.deletedLinkText)
  
  # def testgetLinkCategories(self):
    # assert albatross.getLinkCategories(self.firstLinkText) == ['Humor', 'Pictures']
    # assert not albatross.getLinkCategories(self.deletedLinkText)

  # def testgetLinkDescription(self):
    # assert albatross.getLinkDescription(self.firstLinkText) == 'I believe you have my stapler.'
    # assert not albatross.getLinkDescription(self.deletedLinkText)
    
  # def testcheckLinkDeleted(self):
    # assert albatross.checkLinkDeleted(self.deletedLinkText)
    # assert not albatross.checkLinkDeleted(self.firstLinkText)
    
  # def testcheckLinkExists(self):
    # assert not albatross.checkLinkExists(self.deletedLinkText)
    # assert not self.etiConn.checkLinkExists(self.invalidLinkText)
    # assert self.etiConn.checkLinkExists(self.firstLinkText)
    
  def testcheckTopicValid(self):
    assert self.etiConn.checkTopicValid(self.validTopicText)
    assert not self.etiConn.checkTopicValid(self.invalidTopicText)
    
  def testcheckArchivedTopic(self):
    assert self.etiConn.checkArchivedTopic(self.archivedTopicText)
    assert not self.etiConn.checkArchivedTopic(self.validTopicText)
  
  def testcheckArchivedRedirect(self):
    assert self.etiConn.checkArchivedRedirect(self.archivedRedirectText)
    assert not self.etiConn.checkArchivedRedirect(self.archivedTopicText)
    assert not self.etiConn.checkArchivedRedirect(self.validTopicText)
  
  def testgetTopicID(self):
    assert self.etiConn.getTopicID(self.archivedTopicText) == 6240806
    assert self.etiConn.getTopicID(self.multiPageTopicText) == 6240806
    assert self.etiConn.getTopicID(self.lastPageTopicText) == 6240806
    assert self.etiConn.getTopicID(self.starcraftTopicText) == 6951014
    
  def testgetTopicTitle(self):
    assert self.etiConn.getTopicTitle(self.starcraftTopicText)
    assert not self.etiConn.getTopicTitle(self.invalidTopicText)
    
  def testgetPostID(self):
    assert self.etiConn.getPostID(self.starcraftTopicText) == 81909003
    assert self.etiConn.getPostID(self.multiPageTopicText) == 67880702
    assert self.etiConn.getPostID(self.lastPageTopicText) == 67881347

  def testgetPostUsername(self):
    assert self.etiConn.getPostUsername(self.starcraftTopicText) == 'tsutter810'
    assert self.etiConn.getPostUsername(self.multiPageTopicText) == 'shaunMD'
    assert self.etiConn.getPostUsername(self.lastPageTopicText) == 'KarmaChameleon'

  def testgetPostUserID(self):
    assert self.etiConn.getPostUserID(self.starcraftTopicText) == 4662
    assert self.etiConn.getPostUserID(self.multiPageTopicText) == 4438
    assert self.etiConn.getPostUserID(self.lastPageTopicText) == 97

  def testgetPostDate(self):
    assert self.etiConn.getPostDate(self.starcraftTopicText) == '2/3/2011 04:59:43 PM'
    assert self.etiConn.getPostDate(self.multiPageTopicText) == '4/16/2010 11:40:39 AM'
    assert self.etiConn.getPostDate(self.lastPageTopicText) == '4/16/2010 11:56:53 AM'

  def testgetPostDateUnix(self):
    assert isinstance(self.etiConn.getPostDateUnix(self.starcraftTopicText), int) and self.etiConn.getPostDateUnix(self.starcraftTopicText) > 0
    assert isinstance(self.etiConn.getPostDateUnix(self.multiPageTopicText), int) and self.etiConn.getPostDateUnix(self.multiPageTopicText) > 0
    assert isinstance(self.etiConn.getPostDateUnix(self.lastPageTopicText), int) and self.etiConn.getPostDateUnix(self.lastPageTopicText) > 0
    assert self.etiConn.getPostDateUnix(self.lastPageTopicText) == 1271437013
  
  def testgetPostText(self):
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.starcraftTopicText)[0]) == 'and does that figure in to who you get matched up against on ladder<br />\n'
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.archivedTopicText)[0]) == 'I think Moltar and I are the only ones. <br />\n'
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.lastPageTopicText)[0]) == '<div class="quoted-message" msgid="t,6240806,67881334@0"><div class="message-top">From: <a href="//clouds.endoftheinter.net/profile.php?user=4438">shaunMD</a> | Posted: 4/16/2010 11:56:39 AM</div>I\'m sorry Kiffe, let\'s kiss and make up.</div><br />\nI am so flambuoyantly gay.<br />\n'

  def testgetTopicPageNum(self):
    assert self.etiConn.getTopicPageNum(self.starcraftTopicText) == 1
    assert self.etiConn.getTopicPageNum(self.multiPageTopicText) == 2
    assert self.etiConn.getTopicPageNum(self.lastPageTopicText) == 3

  def testgetTopicNumPages(self):
    assert self.etiConn.getTopicNumPages(self.starcraftTopicText) == 1
    assert self.etiConn.getTopicNumPages(self.multiPageTopicText) == 3
    assert self.etiConn.getTopicNumPages(self.lastPageTopicText) == 3
  
  def testgetTopicPosts(self):
    assert not self.etiConn.getTopicPosts(0)
    assert not self.etiConn.getTopicPosts(1, archived=False)
    assert not self.etiConn.getTopicPosts(self.validTopicID, archived=True)
    assert len(self.etiConn.getTopicPosts(self.validTopicID)) > 0
    
  def testgetLatestTopicID(self):
    assert not self.etiConn.getLatestTopicID(self.emptyTopicSearchList)
    assert isinstance(self.etiConn.getLatestTopicID(self.currentTopicListPage), int) and self.etiConn.getLatestTopicID(self.currentTopicListPage) > 0
    assert isinstance(self.etiConn.getLatestTopicID(self.nwsTopicSearchList), int) and self.etiConn.getLatestTopicID(self.nwsTopicSearchList) > 0
    
  def testgetTopicDateUnix(self):
    assert not self.etiConn.getTopicDateUnix("")
    assert not self.etiConn.getTopicDateUnix("11 suckit 99")
    assert self.etiConn.getTopicDateUnix(self.etiConn.getTopicInfoFromListing(self.currentTopicListPage)['lastPostTime'])
    
  def testgetTopicInfoFromListing(self):
    assert not self.etiConn.getTopicInfoFromListing(self.emptyTopicSearchList)
    assert isinstance(self.etiConn.getTopicInfoFromListing(self.currentTopicListPage), dict) and len(self.etiConn.getTopicInfoFromListing(self.currentTopicListPage)) > 0
    assert isinstance(self.etiConn.getTopicInfoFromListing(self.nwsTopicSearchList), dict) and len(self.etiConn.getTopicInfoFromListing(self.nwsTopicSearchList)) > 0
    
  def testgetTopicList(self):
    assert not self.emptyTopicList
    assert isinstance(self.currentTopicList, list) and len(self.currentTopicList) > 0
    
  def testsearchTopics(self):
    print str(self.nwsTopicSearch)
    self.etiConn.searchTopics(query="NWS", topics=[], recurse=False)
    assert not self.emptyTopicSearch
    assert isinstance(self.nwsTopicSearch, list) and len(self.nwsTopicSearch) > 0
    assert isinstance(self.archivesTopicSearch, list) and len(self.archivesTopicSearch) > 0

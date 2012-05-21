from nose.tools import *
import albatross

class testAlbatrossClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt in the current directory.
    openCredentialsFile = open('credentials.txt')
    credentials = openCredentialsFile.readlines()[0].split(',')
    openCredentialsFile.close()
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Albatross(klass.username, klass.password)
    
    # main page HTML for getEnclosedString test.
    klass.mainPageText = klass.etiConn.getPage(url='https://endoftheinter.net/main.php')

    # link page HTML for link tests.
    klass.firstLinkText = klass.etiConn.getLinkPage(18)
    klass.secondLinkText = klass.etiConn.getLinkPage(389813)
    klass.noLinkLinkText = klass.etiConn.getLinkPage(239465)
    klass.deletedLinkText = klass.etiConn.getLinkPage(362550)
    klass.invalidLinkText = klass.etiConn.getLinkPage(-1)
    
    # topic page and content HTML for topic tests.
    klass.currentTopicListPage = klass.etiConn.getPage(url = 'https://boards.endoftheinter.net/showtopics.php?board=42')
    
    klass.validTopicID = klass.etiConn.getLatestTopicID(klass.currentTopicListPage)
    klass.validTopicText = klass.etiConn.getTopicPage(klass.validTopicID)
    klass.archivedTopicText = klass.etiConn.getTopicPage(6240806, archived=True)
    klass.archivedRedirectTopicText = klass.etiConn.getTopicPage(6240806)
    klass.invalidTopicText = klass.etiConn.getTopicPage(0)
    klass.multiPageTopicText = klass.etiConn.getTopicPage(6240806, pageNum=2, archived=True)
    klass.lastPageTopicText = klass.etiConn.getTopicPage(6240806, pageNum=3, archived=True)
    klass.starcraftTopicText = klass.etiConn.getTopicPage(6951014, boardID=5749, archived=True)
    
    klass.nwsTopicSearchList = klass.etiConn.getPage(url = 'https://boards.endoftheinter.net/search.php?s_aw=NWS&board=42&submit=Submit')
    klass.emptyTopicSearchList = klass.etiConn.getPage(url = 'https://boards.endoftheinter.net/search.php?s_aw=Sdfs0SSODIFHshsd7f6s9d876f9s87f6&board=42&submit=Submit')

    klass.nwsTopicSearch = klass.etiConn.searchTopics(allWords="NWS", topics=[])
    klass.emptyTopicSearch = klass.etiConn.searchTopics(allWords="Sdfs0SSODIFHshsd7f6s9d876f9s87f6", topics=[])

    klass.emptyTopicList = klass.etiConn.getTopicList(archived=False, boardID=-152, pageNum=1, topics=[], recurse=False)
    klass.currentTopicList = klass.etiConn.getTopicList(archived=False, boardID=42, pageNum=1, topics=[], recurse=False)
    
  def testLogin(self):
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
    assert not self.etiConn.checkArchivedTopic(self.archivedRedirectTopicText)
    
  def testcheckArchivedRedirect(self):
    assert self.etiConn.checkArchivedRedirect(self.archivedRedirectTopicText)
    assert not self.etiConn.checkArchivedRedirect(self.archivedTopicText)
    assert not self.etiConn.checkArchivedRedirect(self.validTopicText)
    
  def testgetBoardID(self):
    assert self.etiConn.getBoardID(self.archivedRedirectTopicText) == 42
    assert self.etiConn.getBoardID(self.archivedTopicText) == 42
    assert self.etiConn.getBoardID(self.multiPageTopicText) == 42
    assert self.etiConn.getBoardID(self.lastPageTopicText) == 42
    assert self.etiConn.getBoardID(self.validTopicText) == 42
    assert self.etiConn.getBoardID(self.starcraftTopicText) == 5749
    
  def testgetTopicID(self):
    assert self.etiConn.getTopicID(self.archivedRedirectTopicText) == 6240806
    assert self.etiConn.getTopicID(self.archivedTopicText) == 6240806
    assert self.etiConn.getTopicID(self.multiPageTopicText) == 6240806
    assert self.etiConn.getTopicID(self.lastPageTopicText) == 6240806
    assert self.etiConn.getTopicID(self.starcraftTopicText) == 6951014

  def testgetPostID(self):
    assert not self.etiConn.getPostID(self.archivedRedirectTopicText)
    assert self.etiConn.getPostID(self.starcraftTopicText) == 81909003
    assert self.etiConn.getPostID(self.multiPageTopicText) == 67880702
    assert self.etiConn.getPostID(self.lastPageTopicText) == 67881347

  def testgetPostUsername(self):
    assert not self.etiConn.getPostUsername(self.archivedRedirectTopicText)
    assert self.etiConn.getPostUsername(self.starcraftTopicText) == 'tsutter810'
    assert self.etiConn.getPostUsername(self.multiPageTopicText) == 'shaunMD'
    assert self.etiConn.getPostUsername(self.lastPageTopicText) == 'KarmaChameleon'

  def testgetPostUserID(self):
    assert not self.etiConn.getPostUserID(self.archivedRedirectTopicText)
    assert self.etiConn.getPostUserID(self.starcraftTopicText) == 4662
    assert self.etiConn.getPostUserID(self.multiPageTopicText) == 4438
    assert self.etiConn.getPostUserID(self.lastPageTopicText) == 97

  def testgetPostDate(self):
    assert not self.etiConn.getPostDate(self.archivedRedirectTopicText)
    assert self.etiConn.getPostDate(self.starcraftTopicText) == '2/3/2011 04:59:43 PM'
    assert self.etiConn.getPostDate(self.multiPageTopicText) == '4/16/2010 11:40:39 AM'
    assert self.etiConn.getPostDate(self.lastPageTopicText) == '4/16/2010 11:56:53 AM'

  def testgetPostDateUnix(self):
    assert not self.etiConn.getPostDateUnix(self.archivedRedirectTopicText)
    assert isinstance(self.etiConn.getPostDateUnix(self.starcraftTopicText), int) and self.etiConn.getPostDateUnix(self.starcraftTopicText) > 0
    assert isinstance(self.etiConn.getPostDateUnix(self.multiPageTopicText), int) and self.etiConn.getPostDateUnix(self.multiPageTopicText) > 0
    assert isinstance(self.etiConn.getPostDateUnix(self.lastPageTopicText), int) and self.etiConn.getPostDateUnix(self.lastPageTopicText) > 0

  def testgetPostText(self):
    assert not self.etiConn.getPostText(self.archivedRedirectTopicText)
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.starcraftTopicText)[0]) == 'and does that figure in to who you get matched up against on ladder<br />\n'
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.archivedTopicText)[0]) == 'I think Moltar and I are the only ones. <br />\n'
    assert self.etiConn.getPostText(self.etiConn.getPagePosts(self.lastPageTopicText)[0]) == '<div class="quoted-message" msgid="t,6240806,67881334@0"><div class="message-top">From: <a href="//endoftheinter.net/profile.php?user=4438">shaunMD</a> | Posted: 4/16/2010 11:56:39 AM</div>I\'m sorry Kiffe, let\'s kiss and make up.</div><br />\nI am so flambuoyantly gay.<br />\n'

  def testgetTopicPageNum(self):
    assert not self.etiConn.getTopicPageNum(self.archivedRedirectTopicText)
    assert self.etiConn.getTopicPageNum(self.starcraftTopicText) == 1
    assert self.etiConn.getTopicPageNum(self.multiPageTopicText) == 2
    assert self.etiConn.getTopicPageNum(self.lastPageTopicText) == 3

  def testgetTopicNumPages(self):
    assert not self.etiConn.getTopicNumPages(self.archivedRedirectTopicText)
    assert self.etiConn.getTopicNumPages(self.starcraftTopicText) == 1
    assert self.etiConn.getTopicNumPages(self.multiPageTopicText) == 3
    assert self.etiConn.getTopicNumPages(self.lastPageTopicText) == 3
    assert isinstance(self.etiConn.getTopicNumPages(self.nwsTopicSearchList), int) and self.etiConn.getTopicNumPages(self.nwsTopicSearchList) > 0
    
  def testgetLatestTopicID(self):
    assert not self.etiConn.getLatestTopicID(self.emptyTopicSearchList)
    assert isinstance(self.etiConn.getLatestTopicID(self.currentTopicListPage), int) and self.etiConn.getLatestTopicID(self.currentTopicListPage) > 0
    assert isinstance(self.etiConn.getLatestTopicID(self.nwsTopicSearchList), int) and self.etiConn.getLatestTopicID(self.nwsTopicSearchList) > 0
    
  def testgetTopicInfoFromListing(self):
    assert not self.etiConn.getTopicInfoFromListing(self.emptyTopicSearchList)
    assert isinstance(self.etiConn.getTopicInfoFromListing(self.currentTopicListPage), dict) and len(self.etiConn.getTopicInfoFromListing(self.currentTopicListPage)) > 0
    assert isinstance(self.etiConn.getTopicInfoFromListing(self.nwsTopicSearchList), dict) and len(self.etiConn.getTopicInfoFromListing(self.nwsTopicSearchList)) > 0
    
  def testgetTopicList(self):
    assert not self.emptyTopicList
    assert isinstance(self.currentTopicList, list) and len(self.currentTopicList) > 0
    
  def testsearchTopics(self):
    assert not self.emptyTopicSearch
    assert isinstance(self.nwsTopicSearch, list)

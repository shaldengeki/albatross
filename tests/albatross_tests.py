from nose.tools import *
import albatross
import pycurl
import cStringIO

class testAlbatrossClass(object):
  @classmethod
  def setUpClass(klass):
    openCredentialsFile = open('credentials.txt')
    credentials = openCredentialsFile.readlines()[0].split(',')
    openCredentialsFile.close()
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    
    klass.cookieString = albatross.login(klass.username, klass.password)
    
    klass.firstLinkText = albatross.getLinkPage(18, klass.cookieString)
    klass.secondLinkText = albatross.getLinkPage(389813, klass.cookieString)
    klass.noLinkLinkText = albatross.getLinkPage(239465, klass.cookieString)
    klass.deletedLinkText = albatross.getLinkPage(362550, klass.cookieString)
    
    klass.currentTopicList = albatross.getPage(url = 'https://boards.endoftheinter.net/showtopics.php?board=42', cookieString=klass.cookieString)
    
    klass.validTopicText = albatross.getTopicPage(klass.cookieString, albatross.getLatestTopicID(klass.currentTopicList))
    klass.archivedTopicText = albatross.getTopicPage(klass.cookieString, 6240806, archived=True)
    klass.archivedRedirectTopicText = albatross.getTopicPage(klass.cookieString, 6240806)
    klass.invalidTopicText = albatross.getTopicPage(klass.cookieString, 0)
    klass.multiPageTopicText = albatross.getTopicPage(klass.cookieString, 6240806, pageNum=2, archived=True)
    klass.lastPageTopicText = albatross.getTopicPage(klass.cookieString, 6240806, pageNum=3, archived=True)
    klass.starcraftTopicText = albatross.getTopicPage(klass.cookieString, 6951014, boardID=5749, archived=True)
    
    klass.nwsTopicSearchList = albatross.getPage(url = 'https://boards.endoftheinter.net/search.php?s_aw=NWS&board=42&submit=Submit', cookieString=klass.cookieString)
    klass.nwsTopicSearch = albatross.searchTopics(cookieString=klass.cookieString, allWords="NWS")
    klass.emptyTopicSearch = albatross.searchTopics(cookieString=klass.cookieString, allWords="Sdfs0SSODIFHshsd7f6s9d876f9s87f6")
    
  def testLogin(self):
    assert albatross.login(self.username, self.password)

  def testgetEnclosedString(self):
    assert not albatross.getEnclosedString(self.firstLinkText, 'aspdfasdpofijas', 'aspdfasdpofijas')
    assert albatross.getEnclosedString(self.firstLinkText, '<h1>', '</h1>') == 'I believe you have my stapler'    
  
  def testgetLinkTitle(self):
    assert albatross.getLinkTitle(self.firstLinkText) == 'I believe you have my stapler'
    assert albatross.getLinkTitle(self.noLinkLinkText) == 'K-ON! (COMPLETE with albums)'
    assert albatross.getLinkTitle(self.deletedLinkText) == 'Nodame Cantabile (HD)'
  
  def testgetLinkLink(self):
    assert albatross.getLinkLink(self.firstLinkText) == 'http://stapler.ytmnd.com/'
    assert not albatross.getLinkLink(self.noLinkLinkText)
    assert not albatross.getLinkLink(self.deletedLinkText)
  
  def testgetLinkCreator(self):
    assert albatross.getLinkCreator(self.firstLinkText) == dict([('userid', '1'), ('username', 'LlamaGuy')])
    assert not albatross.getLinkCreator(self.deletedLinkText)
  
  def testgetLinkDate(self):
    assert not albatross.getLinkDate(self.firstLinkText)
    assert albatross.getLinkDate(self.secondLinkText) == '8/23/2011 10:40:27 AM'
    assert not albatross.getLinkDate(self.deletedLinkText)
  
  def testgetLinkCode(self):
    assert albatross.getLinkCode(self.firstLinkText) == 'LL12'
    assert not albatross.getLinkDate(self.deletedLinkText)
  
  def testgetLinkHits(self):
    assert isinstance(albatross.getLinkHits(self.firstLinkText), int) and albatross.getLinkHits(self.firstLinkText) >= 0
    assert not albatross.getLinkHits(self.deletedLinkText)
  
  def testgetLinkRating(self):
    assert isinstance(albatross.getLinkRating(self.firstLinkText), float) and albatross.getLinkRating(self.firstLinkText) >= 0
    assert not albatross.getLinkRating(self.deletedLinkText)
  
  def testgetLinkVotes(self):
    assert isinstance(albatross.getLinkVotes(self.firstLinkText), int) and albatross.getLinkVotes(self.firstLinkText) >= 0
    assert not albatross.getLinkVotes(self.deletedLinkText)

  def testgetLinkRank(self):
    assert isinstance(albatross.getLinkRank(self.firstLinkText), int) and albatross.getLinkRank(self.firstLinkText) >= 0
    assert not albatross.getLinkRank(self.deletedLinkText)
  
  def testgetLinkCategories(self):
    assert albatross.getLinkCategories(self.firstLinkText) == ['Humor', 'Pictures']
    assert not albatross.getLinkCategories(self.deletedLinkText)

  def testgetLinkDescription(self):
    assert albatross.getLinkDescription(self.firstLinkText) == 'I believe you have my stapler.'
    assert not albatross.getLinkDescription(self.deletedLinkText)
    
  def testcheckTopicValid(self):
    assert albatross.checkTopicValid(self.validTopicText)
    assert not albatross.checkTopicValid(self.invalidTopicText)
    
  def testcheckArchivedTopic(self):
    assert albatross.checkArchivedTopic(self.archivedTopicText)
    assert not albatross.checkArchivedTopic(self.validTopicText)
    assert not albatross.checkArchivedTopic(self.archivedRedirectTopicText)
    
  def testcheckArchivedRedirect(self):
    assert albatross.checkArchivedRedirect(self.archivedRedirectTopicText)
    assert not albatross.checkArchivedRedirect(self.archivedTopicText)
    assert not albatross.checkArchivedRedirect(self.validTopicText)
    
  def testgetBoardID(self):
    assert albatross.getBoardID(self.archivedRedirectTopicText) == 42
    assert albatross.getBoardID(self.archivedTopicText) == 42
    assert albatross.getBoardID(self.multiPageTopicText) == 42
    assert albatross.getBoardID(self.lastPageTopicText) == 42
    assert albatross.getBoardID(self.validTopicText) == 42
    assert albatross.getBoardID(self.starcraftTopicText) == 5749
    
  def testgetTopicID(self):
    assert albatross.getTopicID(self.archivedRedirectTopicText) == 6240806
    assert albatross.getTopicID(self.archivedTopicText) == 6240806
    assert albatross.getTopicID(self.multiPageTopicText) == 6240806
    assert albatross.getTopicID(self.lastPageTopicText) == 6240806
    assert albatross.getTopicID(self.starcraftTopicText) == 6951014

  def testgetPostID(self):
    assert not albatross.getPostID(self.archivedRedirectTopicText)
    assert albatross.getPostID(self.starcraftTopicText) == 81909003
    assert albatross.getPostID(self.multiPageTopicText) == 67880702
    assert albatross.getPostID(self.lastPageTopicText) == 67881347

  def testgetPostUsername(self):
    assert not albatross.getPostUsername(self.archivedRedirectTopicText)
    assert albatross.getPostUsername(self.starcraftTopicText) == 'tsutter810'
    assert albatross.getPostUsername(self.multiPageTopicText) == 'shaunMD'
    assert albatross.getPostUsername(self.lastPageTopicText) == 'KarmaChameleon'

  def testgetPostUserID(self):
    assert not albatross.getPostUserID(self.archivedRedirectTopicText)
    assert albatross.getPostUserID(self.starcraftTopicText) == 4662
    assert albatross.getPostUserID(self.multiPageTopicText) == 4438
    assert albatross.getPostUserID(self.lastPageTopicText) == 97

  def testgetPostDate(self):
    assert not albatross.getPostDate(self.archivedRedirectTopicText)
    assert albatross.getPostDate(self.starcraftTopicText) == '2/3/2011 04:59:43 PM'
    assert albatross.getPostDate(self.multiPageTopicText) == '4/16/2010 11:40:39 AM'
    assert albatross.getPostDate(self.lastPageTopicText) == '4/16/2010 11:56:53 AM'

  def testgetPostDateUnix(self):
    assert not albatross.getPostDateUnix(self.archivedRedirectTopicText)
    assert isinstance(albatross.getPostDateUnix(self.starcraftTopicText), int) and albatross.getPostDateUnix(self.starcraftTopicText) > 0
    assert isinstance(albatross.getPostDateUnix(self.multiPageTopicText), int) and albatross.getPostDateUnix(self.multiPageTopicText) > 0
    assert isinstance(albatross.getPostDateUnix(self.lastPageTopicText), int) and albatross.getPostDateUnix(self.lastPageTopicText) > 0

  def testgetPostText(self):
    assert not albatross.getPostText(self.archivedRedirectTopicText)
    assert albatross.getPostText(self.starcraftTopicText) == 'and does that figure in to who you get matched up against on ladder<br />\n'
    assert albatross.getPostText(self.archivedTopicText) == 'I think Moltar and I are the only ones. <br />\n'
    assert albatross.getPostText(self.lastPageTopicText) == '<div class="quoted-message" msgid="t,6240806,67881334@0"><div class="message-top">From: <a href="//endoftheinter.net/profile.php?user=4438">shaunMD</a> | Posted: 4/16/2010 11:56:39 AM</div>I\'m sorry Kiffe, let\'s kiss and make up.</div><br />\nI am so flambuoyantly gay.<br />\n'

  def testgetTopicPageNum(self):
    assert not albatross.getTopicPageNum(self.archivedRedirectTopicText)
    assert albatross.getTopicPageNum(self.starcraftTopicText) == 1
    assert albatross.getTopicPageNum(self.multiPageTopicText) == 2
    assert albatross.getTopicPageNum(self.lastPageTopicText) == 3

  def testgetTopicNumPages(self):
    assert not albatross.getTopicNumPages(self.archivedRedirectTopicText)
    assert albatross.getTopicNumPages(self.starcraftTopicText) == 1
    assert albatross.getTopicNumPages(self.multiPageTopicText) == 3
    assert albatross.getTopicNumPages(self.lastPageTopicText) == 3
    assert isinstance(albatross.getTopicNumPages(self.nwsTopicSearchList), int) and albatross.getTopicNumPages(self.nwsTopicSearchList) > 0
    
  def testgetLatestTopicID(self):
    assert isinstance(albatross.getLatestTopicID(self.currentTopicList), int) and albatross.getLatestTopicID(self.currentTopicList) > 0
    assert isinstance(albatross.getLatestTopicID(self.nwsTopicSearchList), int) and albatross.getLatestTopicID(self.nwsTopicSearchList) > 0
    
  def testsearchTopics(self):
    assert isinstance(self.nwsTopicSearch, list)
    assert not self.emptyTopicSearch
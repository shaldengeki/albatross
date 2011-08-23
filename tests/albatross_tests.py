from nose.tools import *
import albatross

class testAlbatrossClass(object):
  def __init__(self):
    openCredentialsFile = open('credentials.txt')
    credentials = openCredentialsFile.readlines()[0].split(',')
    openCredentialsFile.close()
    
    self.username = credentials[0]
    self.password = credentials[1]
    
    opener = albatross.login(self.username, self.password)
    
    link_page = opener.open('http://links.endoftheinter.net/linkme.php?l=18')
    self.firstLinkText = link_page.read()
    link_page.close()
    
    link_page = opener.open('http://links.endoftheinter.net/linkme.php?l=389813')
    self.secondLinkText = link_page.read()
    link_page.close()
    
    link_page = opener.open('http://links.endoftheinter.net/linkme.php?l=239465')
    self.noLinkLinkText = link_page.read()
    link_page.close()
    
    link_page = opener.open('http://links.endoftheinter.net/linkme.php?l=362550')
    self.deletedLinkText = link_page.read()
    link_page.close()
    
    opener.close()
    
  def testLogin(self):
    assert albatross.login(self.username, self.password)

  def testgetEnclosedString(self):
    assert albatross.getEnclosedString(self.firstLinkText, 'aspdfasdpofijas', 'aspdfasdpofijas') == ''
    assert albatross.getEnclosedString(self.firstLinkText, '<h1>', '</h1>') == 'I believe you have my stapler'    
  
  def testgetLinkTitle(self):
    assert albatross.getLinkTitle(self.firstLinkText) == 'I believe you have my stapler'
    assert albatross.getLinkTitle(self.noLinkLinkText) == 'K-ON! (COMPLETE with albums)'
    assert albatross.getLinkTitle(self.deletedLinkText) == 'Nodame Cantabile (HD)'
  
  def testgetLinkLink(self):
    assert albatross.getLinkLink(self.firstLinkText) == 'http://stapler.ytmnd.com/'
    assert albatross.getLinkLink(self.noLinkLinkText) == ''
    assert not albatross.getLinkLink(self.deletedLinkText)
  
  def testgetLinkCreator(self):
    assert albatross.getLinkCreator(self.firstLinkText) == dict([('userid', '1'), ('username', 'LlamaGuy')])
    assert not albatross.getLinkCreator(self.deletedLinkText)
  
  def testgetLinkDate(self):
    assert albatross.getLinkDate(self.firstLinkText) == ''
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
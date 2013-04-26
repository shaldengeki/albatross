from nose.tools import *
import albatross
import datetime
import pytz

class testLinkClass(object):
  @classmethod
  def setUpClass(self):
    pass
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
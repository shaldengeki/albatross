from nose.tools import *
import albatross
import datetime
import pytz

class testTopicListClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    # topic page and content HTML for topic tests.
    self.currentTopicListPage = self.etiConn.page('https://boards.endoftheinter.net/topics/').html

    self.emptyTopicSearchList = self.etiConn.page('https://boards.endoftheinter.net/topics/?q=abiejgapsodijf').html
    self.cyberlightTopicDict = self.etiConn.topics().parse(self.etiConn.page('https://boards.endoftheinter.net/topics/?q=insanity+enjoy').html)
    self.anonymousTopicDict = self.etiConn.topics().parse(self.etiConn.page('https://boards.endoftheinter.net/topics/Anonymous').html)

    self.nwsTopicSearch = self.etiConn.topics().search(query="NWS")
    self.anonymousTopicSearch = self.etiConn.topics(allowedTags=["Anonymous"]).search(query="")
    self.multiTagTopicSearch = self.etiConn.topics(allowedTags=["LUE", "Anonymous"], forbiddenTags=["Sports", "Gaming"]).search(query="the")
    self.archivesTopicSearch = self.etiConn.topics().search(query="Archived")
    self.emptyTopicSearch = self.etiConn.topics().search(query="abiejgapsodijf")
    self.contradictoryTopicSearch = self.etiConn.topics(allowedTags=["LUE"], forbiddenTags=["LUE"]).search()

    self.emptyTopicList = self.etiConn.topics().search(maxTime=pytz.timezone('America/Chicago').localize(datetime.datetime(1970, 1, 1)), maxID=1)
    self.currentTopicList = self.etiConn.topics().search()
    self.anonymousTopicList = self.etiConn.topics(allowedTags=["Anonymous"]).search()

  def testgetTopicList(self):
    assert isinstance(self.emptyTopicList, albatross.TopicList) and len(self.emptyTopicList) == 0
    assert isinstance(self.currentTopicList, albatross.TopicList) and len(self.currentTopicList) > 0
    assert isinstance(self.anonymousTopicList, albatross.TopicList) and len(self.anonymousTopicList) > 0

  def testgetTopicInfoFromListing(self):
    assert isinstance(self.currentTopicList[0], albatross.Topic)
    assert isinstance(self.cyberlightTopicDict, dict) and len(self.cyberlightTopicDict) > 0 and 'tags' in self.cyberlightTopicDict and 'NWS' in [tag.name for tag in self.cyberlightTopicDict['tags']]
    assert isinstance(self.etiConn.topics().parse(self.currentTopicListPage), dict) and len(self.etiConn.topics().parse(self.currentTopicListPage)) > 0

  @raises(albatross.TopicListError)
  def testgetTopicInfoFromEmptyListing(self):
    self.etiConn.topics().parse(self.emptyTopicSearchList)

  @raises(IndexError)
  def testgetTopicInfoFromEmptyListing(self):
    self.emptyTopicList[0]
    
  def testsearchTopics(self):
    assert isinstance(self.emptyTopicSearch, albatross.TopicList) and len(self.emptyTopicSearch) == 0
    assert isinstance(self.contradictoryTopicSearch, albatross.TopicList) and len(self.contradictoryTopicSearch) == 0
    assert isinstance(self.nwsTopicSearch, albatross.TopicList) and len(self.nwsTopicSearch) > 0
    assert isinstance(self.archivesTopicSearch, albatross.TopicList) and len(self.archivesTopicSearch) > 0
    assert isinstance(self.multiTagTopicSearch, albatross.TopicList) and len(self.multiTagTopicSearch) > 0
    assert isinstance(self.anonymousTopicSearch, albatross.TopicList) and len(self.anonymousTopicSearch) > 0
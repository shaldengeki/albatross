from nose.tools import *
import albatross
import datetime
import pytz

class testTopicListClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    # topic page and content HTML for topic tests.
    klass.currentTopicListPage = klass.etiConn.page('https://boards.endoftheinter.net/topics/').html

    klass.emptyTopicSearchList = klass.etiConn.page('https://boards.endoftheinter.net/topics/?q=abiejgapsodijf').html
    klass.cyberlightTopicDict = klass.etiConn.topics.parse(klass.etiConn.page('https://boards.endoftheinter.net/topics/?q=insanity+enjoy').html)
    klass.anonymousTopicDict = klass.etiConn.topics.parse(klass.etiConn.page('https://boards.endoftheinter.net/topics/Anonymous').html)

    klass.nwsTopicSearch = klass.etiConn.topics.search(query="NWS")
    klass.anonymousTopicSearch = klass.etiConn.topics.search(query="", allowedTags=["Anonymous"])
    klass.multiTagTopicSearch = klass.etiConn.topics.search(query="the", allowedTags=["LUE", "Anonymous"], forbiddenTags=["Sports", "Gaming"])
    klass.archivesTopicSearch = klass.etiConn.topics.search(query="Archived")
    klass.emptyTopicSearch = klass.etiConn.topics.search(query="abiejgapsodijf")
    klass.contradictoryTopicSearch = klass.etiConn.topics.search(allowedTags=["LUE"], forbiddenTags=["LUE"])

    klass.emptyTopicList = klass.etiConn.topics.search(maxTopicTime=pytz.timezone('America/Chicago').localize(datetime.datetime(1970, 1, 1)), maxTopicID=1)
    klass.currentTopicList = klass.etiConn.topics.search()
    klass.anonymousTopicList = klass.etiConn.topics.search(allowedTags=["Anonymous"])

  def testgetTopicList(self):
    assert isinstance(self.emptyTopicList, albatross.TopicList) and len(self.emptyTopicList) == 0
    assert isinstance(self.currentTopicList, albatross.TopicList) and len(self.currentTopicList) > 0
    assert isinstance(self.anonymousTopicList, albatross.TopicList) and len(self.anonymousTopicList) > 0

  def testgetTopicInfoFromListing(self):
    assert isinstance(self.currentTopicList[0], albatross.Topic)
    assert isinstance(self.cyberlightTopicDict, dict) and len(self.cyberlightTopicDict) > 0 and 'tags' in self.cyberlightTopicDict and 'NWS' in [tag.name for tag in self.cyberlightTopicDict['tags']]
    assert isinstance(self.etiConn.topics.parse(self.currentTopicListPage), dict) and len(self.etiConn.topics.parse(self.currentTopicListPage)) > 0

  @raises(albatross.TopicListException)
  def testgetTopicInfoFromEmptyListing(self):
    self.etiConn.topics.parse(self.emptyTopicSearchList)

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
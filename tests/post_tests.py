from nose.tools import *
import albatross
import datetime
import pytz

class testPostClass(object):
  @classmethod
  def setUpClass(klass):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    klass.username = credentials[0]
    klass.password = credentials[1].rstrip()
    klass.etiConn = albatross.Connection(username=klass.username, password=klass.password, loginSite=albatross.SITE_MOBILE)

    klass.centralTimezone = pytz.timezone('America/Chicago')

    klass.validTopic = klass.etiConn.topics.search(allowedTags=["LUE"], forbiddenTags=["Anonymous"])[0]
    klass.validPost = klass.validTopic.posts()[0]
    klass.archivedTopic = klass.etiConn.topic(6240806)
    klass.archivedPost = klass.etiConn.post(67630266, klass.archivedTopic)
    klass.starcraftTopic = klass.etiConn.topic(6951014)
    klass.starcraftPost = klass.etiConn.post(81909003, klass.starcraftTopic)
    klass.anonymousTopic = klass.etiConn.topic(8431797)
    klass.anonymousPost = klass.etiConn.post(124662128, klass.anonymousTopic)

  def testgetPostHTML(self):
    assert isinstance(self.validPost.html, str) or isinstance(self.validPost.html, unicode) and len(self.validPost.html) > 0
    assert self.starcraftPost.html == 'and does that figure in to who you get matched up against on ladder<br />'
    assert self.archivedPost.html == 'I think Moltar and I are the only ones. <br />'
    assert self.anonymousPost.html == "two bra and panty sets, a casual dress, a six pack of panties, and six assorted patterned pantyhose.<br />\n<br />\ni'm really glad i have the opportunity to try this now."

  def testgetPostID(self):
    assert isinstance(self.validPost.id, int) and self.validPost.id > 0
    assert self.starcraftPost.id == 81909003
    assert self.archivedPost.id == 67630266
    assert self.anonymousPost.id == 124662128

  def testgetPostUsername(self):
    assert isinstance(self.validPost.user['name'], str) or isinstance(self.validPost.user['name'], unicode) and len(self.validPost.user['name']) > 0
    assert self.starcraftPost.user['name'] == 'tsutter810'
    assert self.archivedPost.user['name'] == 'Kiffe'
    assert self.anonymousPost.user['name'] == 'Human'

  def testgetPostUserID(self):
    assert isinstance(self.validPost.user['id'], int) and self.validPost.user['id'] > 0
    assert self.starcraftPost.user['id'] == 4662
    assert self.archivedPost.user['id'] == 11689
    assert self.anonymousPost.user['id'] == 0

  def testgetPostDate(self):
    assert isinstance(self.validPost.date, datetime.datetime) and self.validPost.date > datetime.datetime.fromtimestamp(0, tz=self.centralTimezone)
    assert self.starcraftPost.date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)
    assert self.archivedPost.date == datetime.datetime.fromtimestamp(1271042261, tz=self.centralTimezone)
    assert self.anonymousPost.date == datetime.datetime.fromtimestamp(1366924222, tz=self.centralTimezone)
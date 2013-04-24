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

    klass.archivedTopic = klass.etiConn.topic(6240806)
    klass.multiPageTopic = klass.etiConn.topic(6240806, page=2)
    klass.lastPageTopic = klass.etiConn.topic(6240806, page=3)
    klass.starcraftTopic = klass.etiConn.topic(6951014)

  def testgetPostHTML(self):
    assert self.starcraftTopic.posts()[0].html == 'and does that figure in to who you get matched up against on ladder<br />\n'
    assert self.archivedTopic.posts()[0].html == 'I think Moltar and I are the only ones. <br />\n'
    assert self.lastPageTopic.posts()[0].html == '<div class="quoted-message" msgid="t,6240806,67881334@0"><div class="message-top">From: <a href="//endoftheinter.net/profile.php?user=4438">shaunMD</a> | Posted: 4/16/2010 11:56:39 AM</div>I\'m sorry Kiffe, let\'s kiss and make up.</div><br />\nI am so flambuoyantly gay.<br />\n'

  def testgetPostID(self):
    assert self.starcraftTopic.posts()[0].id == 81909003
    assert self.multiPageTopic.posts()[0].id == 67880702
    assert self.lastPageTopic.posts()[0].id == 67881347

  def testgetPostUsername(self):
    assert self.starcraftTopic.posts()[0].user['name'] == 'tsutter810'
    assert self.multiPageTopic.posts()[0].user['name'] == 'shaunMD'
    assert self.lastPageTopic.posts()[0].user['name'] == 'KarmaChameleon'
    # assert self.starcraftTopic.posts()[0].user.name == 'tsutter810'
    # assert self.multiPageTopic.posts()[0].user.name == 'shaunMD'
    # assert self.lastPageTopic.posts()[0].user.name == 'KarmaChameleon'

  def testgetPostUserID(self):
    assert self.starcraftTopic.posts()[0].user['id'] == 4662
    assert self.multiPageTopic.posts()[0].user['id'] == 4438
    assert self.lastPageTopic.posts()[0].user['id'] == 97
    # assert self.starcraftTopic.posts()[0].user.id == 4662
    # assert self.multiPageTopic.posts()[0].user.id == 4438
    # assert self.lastPageTopic.posts()[0].user.id == 97

  def testgetPostDate(self):
    assert self.starcraftTopic.posts()[0].date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)
    assert self.multiPageTopic.posts()[0].date == datetime.datetime.fromtimestamp(1271436039, tz=self.centralTimezone)
    assert self.lastPageTopic.posts()[0].date == datetime.datetime.fromtimestamp(1271437013, tz=self.centralTimezone)
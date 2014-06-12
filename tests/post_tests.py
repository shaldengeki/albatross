from nose.tools import *
import albatross
import datetime
import pytz

class testPostClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.centralTimezone = pytz.timezone('America/Chicago')

    self.validTopic = self.etiConn.topics(allowedTags=["LUE"], forbiddenTags=["Anonymous"]).search()[0]
    self.validPost = self.validTopic.posts()[0]
    self.archivedTopic = self.etiConn.topic(6240806)
    self.archivedPost = self.etiConn.post(67630266, self.archivedTopic)
    self.starcraftTopic = self.etiConn.topic(6951014)
    self.starcraftPost = self.etiConn.post(81909003, self.starcraftTopic)
    self.anonymousTopic = self.etiConn.topic(8431797)
    self.anonymousPost = self.etiConn.post(124662128, self.anonymousTopic)

    self.postWithImage = self.etiConn.post(63243281, self.etiConn.topic(6000000))
    self.postImage = self.etiConn.image(md5="13a40731e96b40ec938a8cf21d898a6c", filename="duck_taped.jpg")
    self.archivedPostWithImage = self.etiConn.post(67880374, self.archivedTopic)
    self.archivedPostImage = self.etiConn.image(md5="e8b39228c9965e28fe5670bcbd420013", filename="drsfyhg.png")
    self.unpostedImage = self.etiConn.image(md5="84427d35982d0a38805d9e2f8d5c82fe", filename="Spring 2014.png")

  @raises(TypeError)
  def testNoIDInvalidPost(self):
    self.etiConn.post()

  @raises(TypeError)
  def testNoTopicInvalidPost(self):
    self.etiConn.post(1)

  @raises(albatross.InvalidPostError)
  def testNegativeInvalidPost(self):
    self.etiConn.post(-1, self.validTopic)

  @raises(albatross.InvalidPostError)
  def testFloatInvalidPost(self):
    self.etiConn.post(1.5, self.validTopic)

  @raises(albatross.InvalidPostError)
  def testIncorrectTopicPost(self):
    self.etiConn.post(81909003, self.etiConn.topic(1)).html

  def testcheckPostValid(self):
    assert isinstance(self.validPost, albatross.Post)

  def testgetPostHTML(self):
    assert isinstance(self.validPost.html, unicode) 
    assert len(self.validPost.html) > 0
    assert self.starcraftPost.html == 'and does that figure in to who you get matched up against on ladder<br />'
    assert self.archivedPost.html == 'I think Moltar and I are the only ones. <br />'
    assert self.anonymousPost.html == "two bra and panty sets, a casual dress, a six pack of panties, and six assorted patterned pantyhose.<br />\n<br />\ni'm really glad i have the opportunity to try this now."

  def testPostContainsText(self):
    assert 'does that figure in to' in self.starcraftPost 
    assert 'OHGODTHISSTRINGDOESNTEXIST' not in self.starcraftPost
    assert 'Moltar and I' in self.archivedPost 
    assert 'HEYNEITHERDOESTHISONE' not in self.archivedPost
    assert "i'm really glad" in self.anonymousPost 
    assert 'GUESSWHATNOTTHISONEEITHER' not in self.anonymousPost

  def testPostContainsImage(self):
    assert self.postImage in self.postWithImage
    assert self.unpostedImage not in self.postWithImage
    assert self.archivedPostImage in self.archivedPostWithImage 
    assert self.unpostedImage not in self.archivedPostWithImage

  def testgetPostSig(self):
    assert self.starcraftPost.sig == """<span class="pr">Big Strange Dojo: Big. Strange -- Vortex.</span>"""
    assert self.archivedPost.sig == """see this is the fundamental flaw with the check check-plus check-minus system<br />\n<a class="l" target="_blank" title="http://www.youtube.com/watch?v=7sMD6W0qhYk" href="http://www.youtube.com/watch?v=7sMD6W0qhYk">http://www.youtube.com/watch?v=7sMD6W0qhYk</a> <span class="pr"><b>gpideal isn't gay.</b></span>"""
    assert self.anonymousPost.sig == ""

  def testgetPostID(self):
    assert isinstance(self.validPost.id, int) 
    assert self.validPost.id > 0
    assert self.starcraftPost.id == 81909003
    assert self.archivedPost.id == 67630266
    assert self.anonymousPost.id == 124662128

  def testgetPostUsername(self):
    assert isinstance(self.validPost.user.name, unicode) 
    assert len(self.validPost.user.name) > 0
    assert self.starcraftPost.user.name == 'tsutter810'
    assert self.archivedPost.user.name == 'Kiffe'
    assert self.anonymousPost.user.name == 'Human'

  def testgetPostUserID(self):
    assert isinstance(self.validPost.user.id, int) 
    assert self.validPost.user.id > 0
    assert self.starcraftPost.user.id == 4662
    assert self.archivedPost.user.id == 11689
    assert self.anonymousPost.user.id == 0

  def testgetPostDate(self):
    assert isinstance(self.validPost.date, datetime.datetime) 
    assert self.validPost.date > datetime.datetime.fromtimestamp(0, tz=self.centralTimezone)
    assert self.starcraftPost.date == datetime.datetime.fromtimestamp(1296773983, tz=self.centralTimezone)
    assert self.archivedPost.date == datetime.datetime.fromtimestamp(1271042261, tz=self.centralTimezone)
    assert self.anonymousPost.date == datetime.datetime.fromtimestamp(1366924222, tz=self.centralTimezone)
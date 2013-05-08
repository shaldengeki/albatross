from nose.tools import *
import albatross
import datetime
import pytz

class testUserClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.centralTimezone = pytz.timezone('America/Chicago')

    self.validUser = albatross.User(self.etiConn, 6731)
    self.llamaGuy = albatross.User(self.etiConn, 1)
    self.bannedUser = albatross.User(self.etiConn, 134)
    self.htmlUser = albatross.User(self.etiConn, 9409)
    self.blankUserName = albatross.User(self.etiConn, 17454)
    self.changedUserName = albatross.User(self.etiConn, 7396)
    self.currentUser = [user for user in self.etiConn.users().search(self.username) if user.name == self.username][0]

    self.lueTag = self.etiConn.tag("LUE")
    self.starcraftTag = self.etiConn.tag("Starcraft")

  @raises(TypeError)
  def testNoIDInvalidUser(self):
    self.etiConn.user()

  @raises(albatross.InvalidUserError)
  def testNegativeInvalidUser(self):
    self.etiConn.user(-1)

  @raises(albatross.InvalidUserError)
  def testFloatInvalidUser(self):
    self.etiConn.user(1.5)

  def testcheckUserValid(self):
    assert isinstance(self.validUser, albatross.User)
    assert isinstance(self.bannedUser, albatross.User)

  def testcheckUserId(self):
    assert isinstance(self.validUser.id, int) and self.validUser.id == 6731
    assert isinstance(self.bannedUser.id, int) and self.bannedUser.id == 134
    assert isinstance(self.htmlUser.id, int) and self.htmlUser.id == 9409
    assert isinstance(self.llamaGuy.id, int) and self.llamaGuy.id == 1
    assert isinstance(self.blankUserName.id, int) and self.blankUserName.id == 17454

  def testcheckUserName(self):
    assert isinstance(self.validUser.name, unicode) and self.validUser.name == u'shaldengeki'
    assert isinstance(self.bannedUser.name, unicode) and self.bannedUser.name == u'junkievegeta'
    assert isinstance(self.htmlUser.name, unicode) and self.htmlUser.name == u'<B>Fox1337</B>'
    assert isinstance(self.llamaGuy.name, unicode) and self.llamaGuy.name == u'LlamaGuy :)'
    assert isinstance(self.blankUserName.name, unicode) and self.blankUserName.name == u''

  def testcheckUserLevel(self):
    assert isinstance(self.validUser.level, int) and self.validUser.level > 0
    assert isinstance(self.bannedUser.level, int) and self.bannedUser.level > 0
    assert isinstance(self.htmlUser.level, int) and self.htmlUser.level == 0
    assert isinstance(self.llamaGuy.level, int) and self.llamaGuy.level == 0
    assert isinstance(self.blankUserName.level, int) and self.blankUserName.level == 0

  def testcheckUserBanned(self):
    assert self.validUser.banned == False
    assert self.llamaGuy.banned == False
    assert self.bannedUser.banned == True
    assert self.blankUserName.banned == True

  def testcheckUserSuspended(self):
    assert self.validUser.suspended == False
    assert self.llamaGuy.suspended == False
    assert self.bannedUser.suspended == False
    assert self.blankUserName.suspended == False

  def testcheckUserNameChanged(self):
    assert self.validUser.formerly == None
    assert isinstance(self.changedUserName.formerly, list) and self.changedUserName.formerly == [u'Valmont', u'William T Riker']
    assert isinstance(self.llamaGuy.formerly, list) and self.llamaGuy.formerly == [u'LlamaGuy']


  def testcheckUserReputation(self):
    assert isinstance(self.blankUserName.reputation, dict) and self.blankUserName.reputation == {}
    assert isinstance(self.llamaGuy.reputation, dict) and self.lueTag in self.llamaGuy.reputation and self.lueTag in self.llamaGuy.reputation and isinstance(self.llamaGuy.reputation[self.lueTag], int) and self.llamaGuy.reputation[self.lueTag] > 0
    assert isinstance(self.llamaGuy.reputation, dict) and self.starcraftTag in self.llamaGuy.reputation and self.starcraftTag in self.llamaGuy.reputation and isinstance(self.llamaGuy.reputation[self.starcraftTag], int) and self.llamaGuy.reputation[self.starcraftTag] > 0

  def testcheckUserGoodTokens(self):
    assert isinstance(self.validUser.goodTokens, int) and self.validUser.goodTokens > 0
    assert isinstance(self.bannedUser.goodTokens, int) and self.bannedUser.goodTokens > 0
    assert isinstance(self.htmlUser.goodTokens, int) and self.htmlUser.goodTokens == 0
    assert isinstance(self.llamaGuy.goodTokens, int) and self.llamaGuy.goodTokens > 0
    assert isinstance(self.blankUserName.goodTokens, int) and self.blankUserName.goodTokens == 0

  def testcheckUserBadTokens(self):
    assert isinstance(self.validUser.badTokens, int) and self.validUser.badTokens > 0
    assert isinstance(self.bannedUser.badTokens, int) and self.bannedUser.badTokens == 0
    assert isinstance(self.htmlUser.badTokens, int) and self.htmlUser.badTokens == 0
    assert isinstance(self.llamaGuy.badTokens, int) and self.llamaGuy.badTokens > 0
    assert isinstance(self.blankUserName.badTokens, int) and self.blankUserName.badTokens == 0

  def testcheckUserTokens(self):
    assert isinstance(self.validUser.tokens, int) and self.validUser.tokens > 0
    assert isinstance(self.bannedUser.tokens, int) and self.bannedUser.tokens > 0
    assert isinstance(self.htmlUser.tokens, int) and self.htmlUser.tokens == 0
    assert isinstance(self.llamaGuy.tokens, int) and self.llamaGuy.tokens > 0
    assert isinstance(self.blankUserName.tokens, int) and self.blankUserName.tokens == 0

  def testcheckUserCreated(self):
    assert isinstance(self.validUser.created, datetime.datetime) and self.validUser.created == self.centralTimezone.localize(datetime.datetime(2004,10,14))
    assert isinstance(self.bannedUser.created, datetime.datetime) and self.bannedUser.created == self.centralTimezone.localize(datetime.datetime(2004,5,9))
    assert isinstance(self.htmlUser.created, datetime.datetime) and self.htmlUser.created == self.centralTimezone.localize(datetime.datetime(2005,9,10))
    assert isinstance(self.llamaGuy.created, datetime.datetime) and self.llamaGuy.created == self.centralTimezone.localize(datetime.datetime(2004,5,8))
    assert isinstance(self.blankUserName.created, datetime.datetime) and self.blankUserName.created == self.centralTimezone.localize(datetime.datetime(2009,9,11))

  def testcheckUserLastActive(self):
    assert isinstance(self.validUser.lastActive, datetime.datetime) and self.validUser.lastActive >= self.centralTimezone.localize(datetime.datetime(2013,4,26))
    assert isinstance(self.bannedUser.lastActive, datetime.datetime) and self.bannedUser.lastActive == self.centralTimezone.localize(datetime.datetime(2005,10,22))
    assert isinstance(self.htmlUser.lastActive, datetime.datetime) and self.htmlUser.lastActive == self.centralTimezone.localize(datetime.datetime(2005,11,21))
    assert isinstance(self.llamaGuy.lastActive, datetime.datetime) and self.llamaGuy.lastActive >= self.centralTimezone.localize(datetime.datetime(2013,4,27))
    assert isinstance(self.blankUserName.lastActive, datetime.datetime) and self.blankUserName.lastActive == self.centralTimezone.localize(datetime.datetime(1969,12,31))

  def testcheckUserActive(self):
    assert self.currentUser.active is True
    assert self.bannedUser.active is False

  def testcheckUserSig(self):
    assert isinstance(self.validUser.sig, unicode) and self.validUser.sig == u"""<i>Not you shaldengeki, over the past few days I've gotten to know you better and they've been the happiest days of my life.</i> -<a target="_blank" href="//wiki.endoftheinter.net/index.php/ilikeballoons">ilikeballoons</a>"""
    assert self.htmlUser.sig == None

  def testcheckUserQuote(self):
    assert isinstance(self.validUser.quote, unicode) and self.validUser.quote == u"""<a class="l" target="_blank" title="http://i1.fdc1.endoftheinter.net/i/t/8608ecf79d4167605f35c1525b7f9c2b/DSCN0939.jpg" href="http://i1.fdc1.endoftheinter.net/i/t/8608ecf79d4167605f35c1525b7f9c2b/DSCN0939.jpg">http://i1.fdc1.endoftheinter<span class="m"><span>.net/i/t/8608ecf79d416760</span></span>5f35c1525b7f9c2b/DSCN0939.jpg</a>"""
    assert self.htmlUser.quote == None
    assert isinstance(self.llamaGuy.quote, unicode) and self.llamaGuy.quote == u"""<span class="spoiler_closed" id="u0_1"><span class="spoiler_on_close"><a class="caption" href="#"><b>&lt;spoiler /&gt;</b></a></span><span class="spoiler_on_open"><a class="caption" href="#">&lt;spoiler&gt;</a>test2<a class="caption" href="#">&lt;/spoiler&gt;</a></span></span><script type="text/javascript">onDOMContentLoaded(function(){new llmlSpoiler($("u0_1"))})</script>"""

  def testcheckUserEmail(self):
    assert isinstance(self.validUser.email, unicode) and self.validUser.email == u"""shaldengeki@gmail.com"""
    assert self.htmlUser.email == None
    assert self.llamaGuy.email == None

  def testcheckUserMessaging(self):
    assert isinstance(self.validUser.im, unicode) and self.validUser.im == u"""AIM: pokearphenage"""
    assert self.htmlUser.im == None
    assert self.llamaGuy.im == None

  def testcheckUserPicture(self):
    assert isinstance(self.validUser.picture, unicode) and self.validUser.picture == u"""//i3.endoftheinter.net/i/n/28a0b50c11fad37bcf6fc07f9c4481bc/qwantz-dinosaur.png"""
    assert self.htmlUser.picture == None
    assert isinstance(self.llamaGuy.picture, unicode) and self.llamaGuy.picture == u"//i1.endoftheinter.net/i/n/097c31cfa7bdafdddb7d603835efeb56/327485.jpg"
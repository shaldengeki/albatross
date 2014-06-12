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
    assert isinstance(self.validUser.id, int)
    assert self.validUser.id == 6731
    
    assert isinstance(self.bannedUser.id, int)
    assert self.bannedUser.id == 134
    
    assert isinstance(self.htmlUser.id, int)
    assert self.htmlUser.id == 9409
    
    assert isinstance(self.llamaGuy.id, int)
    assert self.llamaGuy.id == 1
    
    assert isinstance(self.blankUserName.id, int)
    assert self.blankUserName.id == 17454
    

  def testcheckUserName(self):
    assert isinstance(self.validUser.name, unicode)
    assert self.validUser.name == u'shaldengeki'
    
    assert isinstance(self.bannedUser.name, unicode)
    assert self.bannedUser.name == u'junkievegeta'
    
    assert isinstance(self.htmlUser.name, unicode)
    assert self.htmlUser.name == u'<B>Fox1337</B>'
    
    assert isinstance(self.llamaGuy.name, unicode)
    assert self.llamaGuy.name == u'LlamaGuy :)'

    assert isinstance(self.blankUserName.name, unicode)
    assert self.blankUserName.name == u''
    

  def testcheckUserLevel(self):
    assert isinstance(self.validUser.level, int)
    assert self.validUser.level > 0
    
    assert isinstance(self.bannedUser.level, int)
    assert self.bannedUser.level > 0
    
    assert isinstance(self.htmlUser.level, int)
    assert self.htmlUser.level == 0
    
    assert isinstance(self.llamaGuy.level, int)
    assert self.llamaGuy.level == 0
    
    assert isinstance(self.blankUserName.level, int)
    assert self.blankUserName.level == 0
    

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
    assert isinstance(self.changedUserName.formerly, list)
    assert self.changedUserName.formerly == [u'Valmont', u'William T Riker', u'Noam Chomsky']
    
    assert isinstance(self.llamaGuy.formerly, list)
    assert self.llamaGuy.formerly == [u'LlamaGuy']
    


  def testcheckUserReputation(self):
    assert isinstance(self.blankUserName.reputation, dict)
    assert self.blankUserName.reputation == {}
    
    assert isinstance(self.llamaGuy.reputation, dict)
    assert self.lueTag in self.llamaGuy.reputation
    
    assert self.lueTag in self.llamaGuy.reputation
    
    assert isinstance(self.llamaGuy.reputation[self.lueTag], int)
    
    assert self.llamaGuy.reputation[self.lueTag] > 0
    
    assert isinstance(self.llamaGuy.reputation, dict)
    assert self.starcraftTag in self.llamaGuy.reputation
    
    assert self.starcraftTag in self.llamaGuy.reputation
    
    assert isinstance(self.llamaGuy.reputation[self.starcraftTag], int)
    
    assert self.llamaGuy.reputation[self.starcraftTag] > 0
    

  def testcheckUserGoodTokens(self):
    assert isinstance(self.validUser.goodTokens, int)
    assert self.validUser.goodTokens > 0
    
    assert isinstance(self.bannedUser.goodTokens, int)
    assert self.bannedUser.goodTokens > 0
    
    assert isinstance(self.htmlUser.goodTokens, int)
    assert self.htmlUser.goodTokens == 0
    
    assert isinstance(self.llamaGuy.goodTokens, int)
    assert self.llamaGuy.goodTokens > 0
    
    assert isinstance(self.blankUserName.goodTokens, int)
    assert self.blankUserName.goodTokens == 0
    

  def testcheckUserBadTokens(self):
    assert isinstance(self.validUser.badTokens, int)
    assert self.validUser.badTokens > 0
    
    assert isinstance(self.bannedUser.badTokens, int)
    assert self.bannedUser.badTokens == 0
    
    assert isinstance(self.htmlUser.badTokens, int)
    assert self.htmlUser.badTokens == 0
    
    assert isinstance(self.llamaGuy.badTokens, int)
    assert self.llamaGuy.badTokens > 0
    
    assert isinstance(self.blankUserName.badTokens, int)
    assert self.blankUserName.badTokens == 0
    

  def testcheckUserTokens(self):
    assert isinstance(self.validUser.tokens, int)
    assert self.validUser.tokens > 0
    
    assert isinstance(self.bannedUser.tokens, int)
    assert self.bannedUser.tokens > 0
    
    assert isinstance(self.htmlUser.tokens, int)
    assert self.htmlUser.tokens == 0
    
    assert isinstance(self.llamaGuy.tokens, int)
    assert self.llamaGuy.tokens > 0
    
    assert isinstance(self.blankUserName.tokens, int)
    assert self.blankUserName.tokens == 0
    

  def testcheckUserCreated(self):
    assert isinstance(self.validUser.created, datetime.datetime)
    assert self.validUser.created == self.centralTimezone.localize(datetime.datetime(2004,10,14))
    
    assert isinstance(self.bannedUser.created, datetime.datetime)
    assert self.bannedUser.created == self.centralTimezone.localize(datetime.datetime(2004,5,9))
    
    assert isinstance(self.htmlUser.created, datetime.datetime)
    assert self.htmlUser.created == self.centralTimezone.localize(datetime.datetime(2005,9,10))
    
    assert isinstance(self.llamaGuy.created, datetime.datetime)
    assert self.llamaGuy.created == self.centralTimezone.localize(datetime.datetime(2004,5,8))
    
    assert isinstance(self.blankUserName.created, datetime.datetime)
    assert self.blankUserName.created == self.centralTimezone.localize(datetime.datetime(2009,9,11))
    

  def testcheckUserLastActive(self):
    assert isinstance(self.validUser.lastActive, datetime.datetime)
    assert self.validUser.lastActive >= self.centralTimezone.localize(datetime.datetime(2013,4,26))
    
    assert isinstance(self.bannedUser.lastActive, datetime.datetime)
    assert self.bannedUser.lastActive == self.centralTimezone.localize(datetime.datetime(2005,10,22))
    
    assert isinstance(self.htmlUser.lastActive, datetime.datetime)
    assert self.htmlUser.lastActive == self.centralTimezone.localize(datetime.datetime(2005,11,21))
    
    assert isinstance(self.llamaGuy.lastActive, datetime.datetime)
    assert self.llamaGuy.lastActive >= self.centralTimezone.localize(datetime.datetime(2013,4,27))
    
    assert isinstance(self.blankUserName.lastActive, datetime.datetime)
    assert self.blankUserName.lastActive == self.centralTimezone.localize(datetime.datetime(1969,12,31))
    

  def testcheckUserActive(self):
    assert self.currentUser.active is True
    assert self.bannedUser.active is False

  def testcheckUserSig(self):
    assert isinstance(self.validUser.sig, unicode)
    assert self.validUser.sig == u"""<i>Not you shaldengeki, over the past few days I've gotten to know you better and they've been the happiest days of my life.</i> -<a target="_blank" href="//wiki.endoftheinter.net/index.php/ilikeballoons">ilikeballoons</a>"""
    assert self.htmlUser.sig == None

  def testcheckUserQuote(self):
    assert isinstance(self.validUser.quote, unicode)
    assert self.validUser.quote == u"""<a class="l" target="_blank" title="http://i1.endoftheinter.net/i/n/8608ecf79d4167605f35c1525b7f9c2b/DSCN0939.jpg" href="http://i1.endoftheinter.net/i/n/8608ecf79d4167605f35c1525b7f9c2b/DSCN0939.jpg">http://i1.endoftheinter.net/<span class="m"><span>i/n/8608ecf79d416760</span></span>5f35c1525b7f9c2b/DSCN0939.jpg</a>"""
    
    assert self.htmlUser.quote == None
    assert isinstance(self.llamaGuy.quote, unicode)
    assert self.llamaGuy.quote == u"""<span class="spoiler_closed" id="u0_1"><span class="spoiler_on_close"><a class="caption" href="#"><b>&lt;spoiler /&gt;</b></a></span><span class="spoiler_on_open"><a class="caption" href="#">&lt;spoiler&gt;</a>test2<a class="caption" href="#">&lt;/spoiler&gt;</a></span></span><script type="text/javascript">onDOMContentLoaded(function(){new llmlSpoiler($("u0_1"))})</script>"""
    
  def testcheckUserEmail(self):
    assert isinstance(self.validUser.email, unicode)
    assert self.validUser.email == u"""shaldengeki@gmail.com"""
    
    assert self.htmlUser.email == None
    assert self.llamaGuy.email == None

  def testcheckUserMessaging(self):
    assert isinstance(self.validUser.im, unicode)
    assert self.validUser.im == u"""AIM: pokearphenage"""
    
    assert self.htmlUser.im == None
    assert self.llamaGuy.im == None

  def testcheckUserPicture(self):
    assert isinstance(self.validUser.picture, unicode)
    assert len(self.validUser.picture) > 0
    
    assert self.htmlUser.picture == None
    assert isinstance(self.llamaGuy.picture, unicode)
    assert self.llamaGuy.picture == u"//i1.endoftheinter.net/i/n/097c31cfa7bdafdddb7d603835efeb56/327485.jpg"
    
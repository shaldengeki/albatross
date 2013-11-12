#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    User - User information retrieval and manipulation.
'''

import datetime
import HTMLParser
import pytz
import re
import xml.sax.saxutils

import albatross
import connection

class InvalidUserError(albatross.Error):
  def __init__(self, user):
    super(InvalidUserError, self).__init__()
    self.user = user
  def __str__(self):
    return "\n".join([
        super(InvalidUserError, self).__str__(),
      "ID: " + unicode(self.user.id)
      ])

class User(object):
  '''
  User-loading object for albatross.
  '''
  def __init__(self, conn, id):
    self.connection = conn
    self.id = id
    if not isinstance(self.id, int) or int(self.id) < 0:
      raise InvalidUserError(self)
    self._name = self._level = self._banned = self._suspended = self._formerly = self._reputation = self._goodTokens = self._badTokens = self._tokens = self._created = self._active = self._lastActive = self._sig = self._quote = self._email = self._im = self._picture = None

  def __str__(self):
    if self._created is None:
      self.load()
    return "\n".join([
      "ID: " + unicode(self.id),
      "Name: " + unicode(self.name) + " (" + unicode(self.level) + ")",
      "Formerly: " + unicode(self.formerly),
      "Banned: " + unicode(self.banned),
      "Suspended: " + unicode(self.suspended),
      "Reputation: " + unicode(self.reputation),
      "Tokens:" + unicode(self.tokens),
      "Good Tokens: " + unicode(self.goodTokens),
      "Bad Tokens: " + unicode(self.badTokens),
      "Created: " + self.created.strftime("%m/%d/%Y"),
      "Last Active: " + self.lastActive.strftime("%m/%d/%Y"),
      "Signature:" + unicode(self.sig),
      "Quote: " + unicode(self.quote),
      "Email: " + unicode(self.email),
      "IM:" + unicode(self.im),
      "Picture: " + unicode(self.picture)
      ])

  def __index__(self):
    return self.id

  def __hash__(self):
    return self.id

  def __eq__(self, userID):
    return self.id == userID

  def set(self, attrDict):
    """
    Sets attributes of this user object with keys found in dict.
    """
    for key in attrDict:
      if key == 'id':
        self.id = attrDict[key]
      else:
        setattr(self, "_" + key, attrDict[key])
    return self

  def parse(self, html):
    """
    Parses a user's profile page.
    Returns a dict of attributes.
    """
    attrs = {}
    parser = HTMLParser.HTMLParser()
    centralTime = pytz.timezone("America/Chicago")

    attrs['id'] = int(albatross.getEnclosedString(html, "<td>User ID</td>\s+<td>", r"</td>"))
    attrs['name'] = parser.unescape(albatross.getEnclosedString(html, r'<th colspan="2">Current Information for ', r'</th>'))
    try:
      attrs['level'] = int(albatross.getEnclosedString(html, r"""<td><a href="//endoftheinter\.net/profile\.php\?user=""" + str(attrs['id']) + """\">""" + re.escape(xml.sax.saxutils.escape(attrs['name'])) + """</a> \(""", r'\)'))
    except ValueError:
      # User has a non-integral level.
      attrs['level'] = 0
    matchStatus = albatross.getEnclosedString(html, "<td>Status</td>\s+<td>", r"</td>")
    attrs['banned'] = False
    attrs['suspended'] = False
    if matchStatus:
      if matchStatus == '<b>Banned</b>':
        attrs['banned'] = True
      else:
        attrs['suspended'] = centralTime.localize(datetime.datetime.strptime(albatross.getEnclosedString(matchStatus, '<b>Suspended until:</b> ', ''), "%m/%d/%Y %I:%M:%S %p"))
    attrs['formerly'] = None
    nameChanged = albatross.getEnclosedString(html, "<td>Formerly</td>\s+<td>", "</td>")
    if nameChanged:
      attrs['formerly'] = nameChanged.split(", ")
    attrs['reputation'] = {}
    reputationText = albatross.getEnclosedString(html, r'<td>Reputation</td><td style="line-height:1.6em">', r'</td>')
    if reputationText:
      for repLine in reputationText.split("&bull; "):
        tagName = parser.unescape(albatross.getEnclosedString(repLine, r'">', r'</a>'))
        tagRep = int(re.sub('\([0-9\,]+\)', '', albatross.getEnclosedString(repLine, r':&nbsp;', '').replace('&nbsp;', '')).replace(",", ""))
        attrs['reputation'][self.connection.tag(tagName)] = tagRep
    tokenText = albatross.getEnclosedString(html, '<td>Tokens</td>\s+<td>', '</td>')
    if not tokenText:
      tokenText = 0
    attrs['tokens'] = int(tokenText)
    attrs['goodTokens'] = int(albatross.getEnclosedString(html, '<td>(<a href="tokenlist\.php\?user=' + str(attrs['id']) + '&amp;type=2">)?Good&nbsp;Tokens(</a>)?</td>\s+<td>', '</td>'))
    attrs['badTokens'] = int(albatross.getEnclosedString(html, '<td>(<a href="tokenlist\.php\?user=' + str(attrs['id']) + '&amp;type=1">)?Bad Tokens(</a>)?</td>\s+<td>', '</td>'))
    attrs['created'] = centralTime.localize(datetime.datetime.strptime(albatross.getEnclosedString(html, '<td>Account Created</td>\s+<td>', '</td>'), "%m/%d/%Y"))
    attrs['active'] = bool(re.search('\(online now\)', albatross.getEnclosedString(html, '<td>Last Active</td>\s+<td>', '</td>')))
    attrs['lastActive'] = centralTime.localize(datetime.datetime.strptime(albatross.getEnclosedString(html, '<td>Last Active</td>\s+<td>', '( \(online now\))?</td>'), "%m/%d/%Y"))
    attrs['sig'] = True and albatross.getEnclosedString(html, '<td>Signature</td>\s+<td>', '</td>') or None
    attrs['quote'] = True and albatross.getEnclosedString(html, '<td>Quote</td>\s+<td>', '</td>') or None
    attrs['email'] = True and albatross.getEnclosedString(html, '<td>Email Address</td>\s+<td>', '</td>') or None
    attrs['im'] = True and albatross.getEnclosedString(html, '<td>Instant&nbsp;Messaging</td>\s+<td>', '</td>') or None
    attrs['picture'] = True and albatross.getEnclosedString(html, '<td>Picture</td>\s+<td>\s*<a target="_blank" imgsrc="http:', '" href') or None

    return attrs

  def load(self):
    """
    Fetches user info.
    """
    userPage = self.connection.page('https://endoftheinter.net/profile.php?user=' + unicode(self.id))

    # check to see if this user is valid.
    # if username is not present, then status must be (indicates previously-extant user was banned or suspended)
    if not re.search(r'<th colspan="2">Current Information for .+?</th>', userPage.html) and not re.search(r'<td>Status</td>', userPage.html):
      raise InvalidUserError(self)

    if userPage.authed:
      # hooray, start pulling info.
      self.set(self.parse(userPage.html))
    else:
      raise connection.UnauthorizedError(self.connection)

  @property
  def name(self):
    if self._name is None:
      self.load()
    return self._name

  @property
  def level(self):
    if self._level is None:
      self.load()
    return self._level

  @property
  def formerly(self):
    if self._formerly is None:
      self.load()
    return self._formerly

  @property
  def banned(self):
    if self._banned is None:
      self.load()
    return self._banned

  @property
  def suspended(self):
    if self._suspended is None:
      self.load()
    return self._suspended

  @property
  def reputation(self):
    if self._reputation is None:
      self.load()
    return self._reputation

  @property
  def tokens(self):
    if self._tokens is None:
      self.load()
    return self._tokens

  @property
  def goodTokens(self):
    if self._goodTokens is None:
      self.load()
    return self._goodTokens

  @property
  def badTokens(self):
    if self._badTokens is None:
      self.load()
    return self._badTokens

  @property
  def created(self):
    if self._created is None:
      self.load()
    return self._created

  @property
  def active(self):
    if self._active is None:
      self.load()
    return self._active

  @property
  def lastActive(self):
    if self._lastActive is None:
      self.load()
    return self._lastActive

  @property
  def sig(self):
    if self._sig is None:
      self.load()
    return self._sig

  @property
  def quote(self):
    if self._quote is None:
      self.load()
    return self._quote

  @property
  def email(self):
    if self._email is None:
      self.load()
    return self._email

  @property
  def im(self):
    if self._im is None:
      self.load()
    return self._im

  @property
  def picture(self):
    if self._picture is None:
      self.load()
    return self._picture
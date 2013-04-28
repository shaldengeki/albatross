#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    UserList - User list information retrieval and manipulation.
'''
import calendar
import datetime
import HTMLParser
import pytz
import re
import sys
import urllib
import urllib2

import albatross
import page

class UserListError(albatross.Error):
  def __init__(self, topicList):
    super(UserListError, self).__init__()
    self.topicList = topicList
  def __str__(self):
    return "\n".join([
        super(UserListError, self).__str__()
      ])

class UserList(object):
  '''
  User list-loading object for albatross.
  '''
  def __init__(self, conn):
    self.connection = conn
    self._users = []
    self._userIDs = {}

  def __getitem__(self, index):
    return self.users[index]

  def __delitem__(self, index):
    del self.users[index]

  def __setitem__(self, index, value):
    self.users[index] = value

  def __len__(self):
    return len(self.users)

  def __iter__(self):
    for user in self.users:
      yield user

  def __reversed__(self):
    return self.users[::-1]

  def __contains__(self, user):
    return user.id in self._userIDs

  def parse(self, text):
    """
    Returns a dict of user attributes from a line of a user list, or throws an exception if it doesn't match a user listing regex.
    """
    thisUser = re.search(r'\<a\ href\="//endoftheinter\.net/profile\.php\?user\=(?P<userID>[0-9]+)">(?P<username>.*?)</a></td><td>(?P<created>[0-9\/]*)</td><td>(?P<lastActive>[0-9\/]*)', text)
    if not thisUser:
      raise UserListError(self)
    centralTime =  pytz.timezone('America/Chicago')
    parser = HTMLParser.HTMLParser()

    userID = int(thisUser.group('userID')) if thisUser.group('userID') else None
    username = parser.unescape(thisUser.group('username')) if thisUser.group('username') else None
    created = centralTime.localize(datetime.datetime.strptime(thisUser.group('created'), "%m/%d/%Y")) if thisUser.group('created') else None
    lastActive = centralTime.localize(datetime.datetime.strptime(thisUser.group('lastActive'), "%m/%d/%Y")) if thisUser.group('lastActive') else None

    return dict([('id', userID), ('name', username), ('created', created), ('lastActive', lastActive)])

  def getPageUsers(self, text):
    """
    Takes the HTML of one page of a user listing and returns a list containing the HTML for one user in each element on said page.
    """
    return text.split('<tr><td>')[1:]

  def appendUsers(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a user listing as fed in by pyparallelcurl and appends the users contained within to the current user list.
    """
    if not text:
      thisPage = self.connection.page(url)
      raise page.PageLoadError(thisPage)
    
    thisPage = page.Page(self.connection, url)
    thisPage._html = text
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendPosts, paramArray)
        return

    maxID = paramArray['maxID']
    activeSince = paramArray['activeSince']
    createdSince = paramArray['createdSince']
      
    thisPageUsers = self.getPageUsers(text)
    for userRow in thisPageUsers:
      print isinstance(userRow, str) or isinstance(userRow, unicode)
      newUser = self.connection.user(0).set(self.parse(userRow))
      if newUser.id <= maxID and newUser.lastActive >= activeSince and newUser.created >= createdSince and newUser not in self:
        self._userIDs[newUser] = 1
        self._users.append(newUser)

  def search(self, query="", maxID=None, activeSince=None, createdSince=None, startPageNum=None, endPageNum=None, recurse=False):
    """
    Searches for users using given parameters, and returns the current user listing object
    Performs operation in parallel.
    """
    self._users = []
    self._userIDs = {}

    maxID = float("inf") if maxID is None else int(maxID)
    activeSince = pytz.timezone('America/Chicago').localize(datetime.datetime(1970, 1, 1)) if activeSince is None else activeSince
    createdSince = pytz.timezone('America/Chicago').localize(datetime.datetime(1970, 1, 1)) if createdSince is None else createdSince
    startPageNum = 1 if startPageNum is None else int(startPageNum)

    paramArray = {'maxID': maxID, 'activeSince': activeSince, 'createdSince': createdSince}

    if endPageNum is None or not recurse:
      # fetch first page to grab number of pages, and grab users while we're at it.
      userListParams = urllib.urlencode([('user', unicode(query)), ('page', str(startPageNum))])
      firstUrl = 'https://endoftheinter.net/userlist.php?' + userListParams
      firstUserPage = self.connection.page(firstUrl)
      self.appendUsers(firstUserPage.html, firstUrl, None, paramArray)

      endPageNum = int(albatross.getEnclosedString(firstUserPage.html, r'Page ' + str(startPageNum) + r' of <span>', r'</span>'))

      # increment start page num.
      startPageNum += 1
    else:
      endPageNum = int(endPageNum)

    if not recurse:
      return self

    # now loop over all the other pages (if there are any)
    for pageNum in range(startPageNum, endPageNum+1):
      userListParams = urllib.urlencode([('user', unicode(query)), ('page', str(pageNum))])
      self.connection.parallelCurl.startrequest('https://endoftheinter.net/userlist.php?' + userListParams, self.appendUsers, paramArray)
    self.connection.parallelCurl.finishallrequests()
    self._users = sorted(self._users, key=lambda userObject: userObject.id)
    return self

  @property
  def users(self):
    return self._users
#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Connection - provides primary interface to ETI, and spawns topics / tags / links / users / etc.
'''
import cStringIO
import os
import pycurl
import pyparallelcurl
import re
import urllib

import albatross
from page import Page
from topic import Topic
from topiclist import TopicList
from tag import Tag
from taglist import TagList
from post import Post
from image import Image
from user import User
from userlist import UserList

class UnauthorizedError(albatross.Error):
  def __init__(self, cxn):
    super(UnauthorizedError, self).__init__()
    self.connection = cxn
  def __str__(self):
    return "\n".join([
        super(UnauthorizedError, self).__str__()
      ])

class Connection(object):
  '''
  Provides connection to ETI.
  '''
  def __init__(self, username="", password="", cookieString="", cookieFile="", reauth=None, loginSite=None, concurrents=20):
    """
    Connection constructor.
    Expects either a username + password pair, or a cookie string and possibly a cookie file to read updated cookie strings from.
    If a username + password or cookie string + file pair is provided, then will attempt to reauthenticate if a logout is detected.
    To prevent this behavior, call the constructor with the reauth argument set to False.
    """
    self.username = username
    self.password = password
    self.loginSite = loginSite if loginSite is not None else albatross.SITE_MAIN
    self.cookieFile = cookieFile
    self.concurrents = int(concurrents)
    self.numRequests = 0
    self.csrfKey = None
    self.parallelCurlOptions = {}
    self.parallelCurl = self.cookieString = None
    if username and password:
      self.cookieString = self.login()
      self.reauth = True
    elif cookieString:
      self.cookieString = cookieString
      if os.path.exists(self.cookieFile):
        self.reauth = True
      else:
        self.reauth = False
    if reauth is not None:
      self.reauth = bool(reauth)
    if not self.cookieString or not self.loggedIn():
      print "Warning: invalid credentials provided."
      raise UnauthorizedError(self)
    self.setParallelCurlObject()
    
  def parseCookieHeader(self, string):
    """
    Given a cookie response header returned by pyCurl, return a string of cookie key/values.
    """
    
    string_array = unicode(string).split("\r\n")
    cookieList = []
    for line in string_array:
      if line.startswith("Set-Cookie:"):
        cookieList.append('='.join(line[11:-1].strip().split(";")[0].split("=")))
        
    cookieString = '; '.join(cookieList)
    return cookieString
  
  def login(self):
    """
    Logs into LL using connection's username and password, returning the resultant cookie string.
    """
    response = cStringIO.StringIO()
    loginHeaders = pycurl.Curl()
    
    loginHeaders.setopt(pycurl.SSL_VERIFYPEER, False)
    loginHeaders.setopt(pycurl.SSL_VERIFYHOST, False)
    loginHeaders.setopt(pycurl.POST, 1)
    loginHeaders.setopt(pycurl.HEADER, True)
    loginHeaders.setopt(pycurl.URL, self.loginSite["url"]+'index.php')
    loginHeaders.setopt(pycurl.POSTFIELDS, urllib.urlencode(dict([(self.loginSite["fields"]["username"], unicode(self.username).encode('utf-8')), (self.loginSite["fields"]["password"], unicode(self.password).encode('utf-8')), ('r', '')])))
    loginHeaders.setopt(pycurl.USERAGENT, 'Albatross')
    loginHeaders.setopt(pycurl.WRITEFUNCTION, response.write)
    
    try:
      loginHeaders.perform()
      loginHeaders.close()
    except:
      return False
    
    cookieHeader = response.getvalue()
    if re.search(r'Sie bitte 15 Minuten', cookieHeader) or not re.search(r'session=', cookieHeader):
      return False

    cookieString = self.parseCookieHeader(cookieHeader)
    self.cookieString = cookieString
    self.setParallelCurlObject()
    return cookieString
  
  @property
  def user_id(self):
    cookie_parts = self.cookieString.split('; ')
    user_id = None
    for part in cookie_parts:
      key,value = part.split('=')
      if key == "userid":
        user_id = int(value)
    return user_id

  def setParallelCurlObject(self):
    """
    (Re)sets the parallelCurl object to use the current cookieString.
    """
    self.parallelCurlOptions = {
      pycurl.SSL_VERIFYPEER: False,
      pycurl.SSL_VERIFYHOST: False,
      pycurl.FOLLOWLOCATION: True, 
      pycurl.COOKIE: self.cookieString.encode('utf-8') if self.cookieString else u""
    }
    try:
      self.parallelCurl.setoptions(self.parallelCurlOptions)
    except AttributeError:
      self.parallelCurl = pyparallelcurl.ParallelCurl(self.concurrents, self.parallelCurlOptions)
    
  def reauthenticate(self):
    """
    Reauthenticates and resets authentication attributes if need be and reauth attribute is True.
    """
    if self.reauth:
      cookieString = None
      if self.loggedIn():
        return True
      if self.username and self.password:
        cookieString = self.login()
      elif os.path.exists(self.cookieFile):
        cookieString = open(self.cookieFile, 'r').readline().strip('\n')
      if cookieString:
        self.cookieString = cookieString
        if self.username and self.password and self.cookieFile and os.path.exists(self.cookieFile):
          with open(self.cookieFile, 'w') as f:
            f.write(self.cookieString)
        self.setParallelCurlObject()
    return self.loggedIn()
  
  def etiUp(self, retries=10):
    """
    Checks to see if ETI is having server / DNS issues.
    Note that this is necessarily unable to distinguish issues on your end from issues on ETI's end!
    Returns a boolean.
    """
    for x in range(retries): # Limit the number of retries.
      header = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, "https://endoftheinter.net/index.php")
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, unicode(self.cookieString).encode('utf-8'))
      pageRequest.setopt(pycurl.HEADERFUNCTION, header.write)
      try:
        pageRequest.perform()
        requestCode = pageRequest.getinfo(pageRequest.HTTP_CODE)
        pageRequest.close()
      except:
        continue
      # check to see if ETI is acting up.
      return requestCode not in {0:1, 404:1, 500:1, 501:1, 502:1, 503:1, 504:1}
    return False

  def loggedIn(self):
    """
    Checks if the current cookie string is still valid.
    Returns boolean value reflecting this.
    """
    
    mainPageHTML = self.page('https://endoftheinter.net/main.php', authed=False).html
    if not mainPageHTML or 'stats.php">Stats</a>' not in mainPageHTML:
      return False
    else:
      return True
    
  def page(self, url, authed=True):
    return Page(self, url, authed)

  def topics(self, allowedTags=None, forbiddenTags=None):
    return TopicList(self, allowedTags=allowedTags, forbiddenTags=forbiddenTags)

  def topic(self, id, page=1):
    return Topic(self, id, page=page)

  def tags(self, tags=None, active=False):
    return TagList(self, tags=tags, active=active)

  def tag(self, name):
    return Tag(self, name)

  def post(self, id, topic):
    return Post(self, id, topic)

  def user(self, id):
    return User(self, id)

  def users(self):
    return UserList(self)

  def image(self, md5, filename):
    return Image(self, md5, filename)
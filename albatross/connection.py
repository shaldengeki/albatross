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

class UnauthorizedError(albatross.Error):
  def __init__(self, cxn):
    super(UnauthorizedError, self).__init__()
    self.connection = cxn
  def __str__(self):
    return "\n".join([
        str(super(UnauthorizedError, self))
      ])

class Connection(object):
  '''
  Provides connection to ETI.
  '''
  def __init__(self, username="", password="", cookieString="", cookieFile="", reauth=None, loginSite=None, num_requests=20):
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
    self.num_requests = num_requests
    self.parallelCurlOptions = {}
    self.parallelCurl = None
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
    self.setParallelCurlObject()
    
  def parseCookieHeader(self, string):
    """
    Given a cookie response header returned by pyCurl, return an array of cookie key/values.
    """
    
    string_array = str(string).split("\r\n")
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
    loginHeaders.setopt(pycurl.POSTFIELDS, urllib.urlencode(dict([(self.loginSite["fields"]["username"], str(self.username)), (self.loginSite["fields"]["password"], str(self.password)), ('r', '')])))
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
  
  def setParallelCurlObject(self):
    """
    (Re)sets the parallelCurl object to use the current cookieString.
    """
    self.parallelCurlOptions = {
      pycurl.SSL_VERIFYPEER: False,
      pycurl.SSL_VERIFYHOST: False,
      pycurl.FOLLOWLOCATION: True, 
      pycurl.COOKIE: self.cookieString
    }
    try:
      self.parallelCurl.setoptions(self.parallelCurlOptions)
    except AttributeError:
      self.parallelCurl = pyparallelcurl.ParallelCurl(self.num_requests, self.parallelCurlOptions)
    
  def reauthenticate(self):
    """
    Reauthenticates and resets authentication attributes if need be and reauth attribute is True.
    """
    if self.reauth:
      if self.loggedIn():
        return True
      if self.username and self.password:
        cookieString = self.login()
      elif os.path.exists(self.cookieFile):
        cookieString = open(self.cookieFile, 'r').readline().strip('\n')
      if cookieString and cookieString != self.cookieString:
        self.cookieString = cookieString
        self.setParallelCurlObject()
        return True
    return False
  
  def etiUp(self, retries=10):
    """
    Checks to see if ETI is having server / DNS issues.
    Returns a boolean.
    """
    for x in range(retries): # Limit the number of retries.
      header = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, "https://endoftheinter.net/index.php")
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, str(self.cookieString))
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

  @property
  def topics(self):
    return TopicList(self)

  def topic(self, id, page=1):
    return Topic(self, id, page=page)

  def tags(self, tags=None, active=False):
    return TagList(self, tags=tags, active=active)

  def tag(self, name):
    return Tag(self, name)
#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Topic - Topic information retrieval and manipulation.
'''

import datetime
import pytz
import re
import urllib

import albatross
import connection
import page
import post

class ArchivedTopicException(Exception):
  pass

class InvalidTopicException(Exception):
  pass

class Topic(object):
  '''
  Topic-loading object for albatross.
  '''
  def __init__(self, conn, id, page=1):
    self.connection = conn
    self.id = int(id)
    self.page = page
    self._archived = None
    self._date = None
    self._title = None
    self._pages = None
    self._posts = None
    self._postIDs = {}

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + str(self.id) + " (Archived: " + str(self.archived) + ")",
      "Title: " + str(self.title),
      "Page: " + str(self.page) + "/" + str(self.pages),
      "Posts:" + str(len(self.posts)),
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p")
      ])

  def set(self, attrDict):
    """
    Sets attributes of this topic object with keys found in dict.
    """
    for key in attrDict:
      setattr(self, "_" + key, attrDict[key])
    return self

  def load(self):
    """
    Fetches topic info.
    """
    if self._archived:
      subdomain="archives"
    else:
      subdomain="boards"
    topicPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + str(self.id))
    # check to see if this page is valid.
    if re.search(r'<h2><em>This topic has been archived\. No additional messages may be posted\.</em></h2>', topicPage.html) or re.search(r'HTTP\/1\.1 302 Moved Temporarily', topicPage.header):
      # topic is archived.
      if self._archived is None:
        self._archived = True
        topicPage = self.connection.page('https://archives.endoftheinter.net/showmessages.php?topic=' + str(self.id))
      elif self._archived is False:
        raise ArchivedTopicException("ID " + str(self.id))
    elif self._archived is None:
      self._archived = False
    if not re.search(r'Page\ 1\ of\ ', topicPage.html):
      raise InvalidTopicException("ID " + str(self.id))

    if topicPage.authed:
      # hooray, start pulling info.
      self._title = albatross.getEnclosedString(topicPage.html, r'\<h1\>', r'\<\/h1\>')
      self._date = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(albatross.getEnclosedString(topicPage.html, r'<b>Posted:</b> ', r' \| '), "%m/%d/%Y %I:%M:%S %p"))
      self._pages = int(albatross.getEnclosedString(topicPage.html, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page \d+ of <span>', r'</span>'))
    else:
      raise connection.UnauthorizedException("ID " + str(self.id))

  @property
  def date(self):
    if self._date is None:
      self.load()
    return self._date
  @date.setter
  def date(self, stamp):
    self._date = stamp

  @property
  def title(self):
    if self._title is None:
      self.load()
    return self._title

  @property
  def archived(self):
    if self._archived is None:
      self.load()
    return self._archived

  @property
  def pages(self):
    if self._pages is None:
      self.load()
    return self._pages

  def getPagePosts(self, text):
    """
    Takes the HTML of one page of a topic or link and returns a list containing the HTML for one post in each element on said page.
    """
    return text.split('</td></tr></table></div>')[:-1]

  def appendPosts(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a topic message listing as fed in by pyparallelcurl and appends the posts contained within to the current topic's posts.
    """
    if not text:
      raise page.PageLoadException(url)
    
    thisPage = page.Page(self.connection, url)
    thisPage._html = text
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendPosts, paramArray)
        return
      
    # parse this page and append posts to post list.
    thisPagePosts = self.getPagePosts(text)
    for postRow in thisPagePosts:
      newPost = post.Post(self.connection, 0, self)
      newPost.set(newPost.parse(postRow))
      if newPost.id not in self._postIDs:
        self._postIDs[newPost.id] = 1
        self._posts.append(newPost)

  def getPosts(self, endPageNum=None, userID=None):
    """
    Return a list of post objects in this topic, starting from the current topic page.
    Performs operation in parallel.
    """
    if self.archived:
      topicSubdomain = "archives"
    else:
      topicSubdomain = "boards"
    
    # since we've already fetched the first page's posts (from load), increment start page by one.
    # self.page += 1

    if endPageNum is None:
      endPageNum = self.pages

    self._posts = []
    # now loop over all the other pages (if there are any)
    for pageNum in range(self.page, int(endPageNum)+1):
      topicPageParams = urllib.urlencode([('topic', str(self.id)), ('u', str(userID)), ('page', str(pageNum))])
      self.connection.parallelCurl.startrequest('https://' + topicSubdomain + '.endoftheinter.net/showmessages.php?' + topicPageParams, self.appendPosts)
    self.connection.parallelCurl.finishallrequests()

    self._posts = sorted(self._posts, key=lambda postObject: postObject.id)

  @property
  def posts(self, user=None, page=None):
    if self._posts is None:
      self.getPosts()
    filteredPosts = [postObject for postObject in self._posts if user is None or postObject.user is user]
    if page is not None:
      return filteredPosts[((page-1)*50):(page*50)]
    return filteredPosts
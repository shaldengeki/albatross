#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Topic - Topic information retrieval and manipulation.
'''

import datetime
import HTMLParser
import pytz
import re
import urllib
import urllib2

import albatross
import connection
import page

class InvalidTopicError(albatross.Error):
  def __init__(self, topic):
    super(InvalidTopicError, self).__init__()
    self.topic = topic
  def __str__(self):
    return "\n".join([
        super(InvalidTopicError, self).__str__(),
      "TopicID: " + str(self.topic.id),
      "Page: " + str(self.topic.page)
      ])

class ArchivedTopicError(InvalidTopicError):
  def __str__(self):
    return "\n".join([
        super(ArchivedTopicError, self).__str__(),
      "Archived: " + str(self._archived)
      ])

import post
import taglist

class Topic(object):
  '''
  Topic-loading object for albatross.
  '''
  def __init__(self, conn, id, page=1):
    self.connection = conn
    self.id = int(id)
    self.page = page
    self._closed = None
    self._archived = None
    self._date = None
    self._title = None
    self._user = None
    self._pages = None
    self._posts = None
    self._postIDs = {}
    self._postCount = None
    self._tags = None
    self._lastPostTime = None

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + str(self.id) + " (Archived: " + str(self.archived) + ")",
      "Title: " + str(self.title),
      "Tags: " + ", ".join(self.tags._tagNames),
      "Page: " + str(self.page) + "/" + str(self.pages),
      "Posts:" + str(self.postCount),
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p")
      ])

  def set(self, attrDict):
    """
    Sets attributes of this topic object with keys found in dict.
    """
    for key in attrDict:
      if key == 'id':
        self.id = attrDict[key]
      elif key == 'page':
        self.page = attrDict[key]
      else:
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
        subdomain = "archives"
        topicPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + str(self.id))
      elif self._archived is False:
        raise ArchivedTopicError(self)
    elif self._archived is None:
      self._archived = False
    if not re.search(r'Page\ 1\ of\ ', topicPage.html):
      raise InvalidTopicError(self)

    if topicPage.authed:
      # hooray, start pulling info.
      parser = HTMLParser.HTMLParser()
      self._title = parser.unescape(albatross.getEnclosedString(topicPage.html, r'\<h1\>', r'\<\/h1\>'))
      self._date = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(albatross.getEnclosedString(topicPage.html, r'<b>Posted:</b> ', r' \| '), "%m/%d/%Y %I:%M:%S %p"))
      userID = int(albatross.getEnclosedString(topicPage.html, r'<div class="message-top"><b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">'))
      username = parser.unescape(True and albatross.getEnclosedString(topicPage.html, r'<div class="message-top"><b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=' + str(userID) + r'">', r'</a>') or 'Human')
      self._user = {'id': userID, 'name': username}
      self._pages = int(albatross.getEnclosedString(topicPage.html, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page \d+ of <span>', r'</span>'))
      self._closed = self._archived
      tagNames = [urllib2.unquote(albatross.getEnclosedString(tagEntry, '<a href="/topics/', r'">')) for tagEntry in albatross.getEnclosedString(topicPage.html, r"<h2><div", r"</div></h2>").split(r"</a>")[:-1] if not tagEntry.startswith(' <span')]
      # we need to process tag names
      # e.g. remove enclosing square braces and decode html entities.
      cleanedTagNames = []
      for tagName in tagNames:
        if tagName.startswith("[") and tagName.endswith("]"):
          tagName = tagName[1:-1]
        cleanedTagNames.append(parser.unescape(tagName.replace("_", " ")))
      self._tags = taglist.TagList(self.connection, tags=cleanedTagNames)
      lastPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + str(self.id) + '&page=' + str(self._pages))
      if lastPage.authed:
        lastPagePosts = self.getPagePosts(lastPage.html)
        lastPost = post.Post(self.connection, 0, self)
        lastPost = lastPost.set(lastPost.parse(lastPagePosts[-1]))
        self._lastPostTime = lastPost.date
      else:
        raise connection.UnauthorizedError(self.connection)
    else:
      raise connection.UnauthorizedError(self.connection)

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
  def closed(self):
    if self._closed is None:
      self.load()
    return self._closed

  @property
  def pages(self):
    if self._pages is None:
      self.load()
    return self._pages

  @property
  def tags(self):
    if self._tags is None:
      self.load()
    return self._tags

  @property
  def user(self):
    if self._user is None:
      self.load()
    return self._user

  @property
  def lastPostTime(self):
    if self._lastPostTime is None:
      self.load()
    return self._lastPostTime

  def getPagePosts(self, text):
    """
    Takes the HTML of one page of a topic or link and returns a list containing the HTML for one post in each element on said page.
    """
    return text.split('</td><td class="userpic">')[:-1]

  def appendPosts(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a topic message listing as fed in by pyparallelcurl and appends the posts contained within to the current topic's posts.
    """
    if not text:
      thisPage = page.Page(url)
      raise page.PageLoadError(thisPage)
    
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

  def posts(self, user=None, page=None):
    if self._posts is None:
      self.getPosts()
    filteredPosts = [postObject for postObject in self._posts if user is None or postObject.user is user]
    if page is not None:
      return filteredPosts[((page-1)*50):(page*50)]
    return filteredPosts

  @property
  def postCount(self, user=None, page=None):
    if self._postCount is None:
      self._postCount = len(self.posts())
    return self._postCount
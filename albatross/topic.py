#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Topic - Topic information retrieval and manipulation.
'''

import bs4
import datetime
import HTMLParser
import pytz
import re
import urllib
import urllib2

import albatross
import connection
import page
import base
from image import parse_imagemap

class InvalidTopicError(albatross.Error):
  def __init__(self, topic):
    super(InvalidTopicError, self).__init__()
    self.topic = topic
  def __str__(self):
    return "\n".join([
        super(InvalidTopicError, self).__str__(),
      "TopicID: " + unicode(self.topic.id),
      "Page: " + unicode(self.topic.page)
      ])

class ArchivedTopicError(InvalidTopicError):
  def __str__(self):
    return "\n".join([
        super(ArchivedTopicError, self).__str__(),
      "Archived: " + unicode(self.topic._archived)
      ])

class TopicPermissionError(InvalidTopicError):
  pass

class ClosedTopicError(InvalidTopicError):
  pass

class Topic(base.Base):
  '''
  Topic-loading object for albatross.
  '''
  def __init__(self, conn, id, page=1):
    super(Topic, self).__init__(conn)
    self.id = id
    self.page = page
    if not isinstance(id, int) or int(id) < 1:
      raise InvalidTopicError(self)
    self._closed = None
    self._archived = None
    self._date = None
    self._title = None
    self._user = None
    self._pages = None
    self._posts = None
    self._postCount = None
    self._tags = None
    self._lastPostTime = None
    self._csrfKey = None
    self._images = None
    self._postIDs = {}

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + unicode(self.id) + " (Archived: " + unicode(self.archived) + ")",
      "Title: " + unicode(self.title),
      "Tags: " + ", ".join(self.tags._tagNames),
      "Page: " + unicode(self.page) + "/" + unicode(self.pages),
      "Posts:" + unicode(self.postCount),
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p")
      ])

  def __len__(self):
    return len(self.posts())

  def __contains__(self, post):
    return post.id in self._postIDs

  def __index__(self):
    return self.id

  def __hash__(self):
    return self.id

  def __eq__(self, topic):
    return self.id == topic.id

  def set(self, attrDict):
    """
    Sets attributes of this topic object with keys found in dict.
    """
    super(Topic, self).set(attrDict)
    if hasattr(self, '_page'):
      self.page = self._page
      del self._page
    return self

  def parse(self, html):
    """
    Given the HTML of a topic page, returns a dict of attributes.
    """

    attrs = {}
    parser = HTMLParser.HTMLParser()

    soup = bs4.BeautifulSoup(html)

    attrs['archived'] = bool(re.search(r'<h2><em>This topic has been archived\. No additional messages may be posted\.</em></h2>', html))

    subdomain = "archives" if attrs['archived'] else "boards"

    attrs['title'] = parser.unescape(albatross.getEnclosedString(html, r'\<h1\>', r'\<\/h1\>'))
    attrs['date'] = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(albatross.getEnclosedString(html, r'<b>Posted:</b> ', r' \| '), "%m/%d/%Y %I:%M:%S %p"))
    userID = int(albatross.getEnclosedString(html, r'<div class="message-top"><b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">'))
    username = parser.unescape(True and albatross.getEnclosedString(html, r'<div class="message-top"><b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=' + unicode(userID) + r'">', r'</a>') or 'Human')
    attrs['user'] = self.connection.user(userID).set({'name': username})
    attrs['pages'] = int(albatross.getEnclosedString(html, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page \d+ of <span>', r'</span>'))
    attrs['closed'] = attrs['archived']
    tagNames = [urllib2.unquote(albatross.getEnclosedString(tagEntry, '<a href="/topics/', r'">')) for tagEntry in albatross.getEnclosedString(html, r"<h2><div", r"</div></h2>").split(r"</a>")[:-1] if not tagEntry.startswith(' <span')]
    # we need to process tag names
    # e.g. remove enclosing square braces and decode html entities.
    cleanedTagNames = []
    for tagName in tagNames:
      if tagName.startswith("[") and tagName.endswith("]"):
        tagName = tagName[1:-1]
      cleanedTagNames.append(parser.unescape(tagName.replace("_", " ")))
    attrs['tags'] = self.connection.tags(tags=cleanedTagNames)
    lastPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + unicode(self.id) + '&page=' + unicode(attrs['pages']))
    if lastPage.authed:
      lastPagePosts = self.getPagePosts(lastPage.html)
      lastPost = self.connection.post(1, self)
      lastPost = lastPost.set(lastPost.parse(lastPagePosts[-1]))
      attrs['lastPostTime'] = lastPost.date
    csrfTag = soup.find("input", {"name": "h"})
    if csrfTag:
      attrs['csrfKey'] = csrfTag.get('value')
    return attrs

  def load(self):
    """
    Fetches topic info.
    """
    if self._archived:
      subdomain="archives"
    else:
      subdomain="boards"
    topicPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + unicode(self.id))

    if re.search(r'<h1>Error</h1><em>You are not authorized to view messages on this board\.</em>', topicPage.html):
      raise TopicPermissionError(self)

    # check to see if this page is valid.
    if re.search(r'<h2><em>This topic has been archived\. No additional messages may be posted\.</em></h2>', topicPage.html) or re.search(r'HTTP\/1\.1 302 Moved Temporarily', topicPage.header):
      # topic is archived.
      if self._archived is None:
        self._archived = True
        subdomain = "archives"
        topicPage = self.connection.page('https://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + unicode(self.id))
      elif self._archived is False:
        raise ArchivedTopicError(self)
    elif self._archived is None:
      self._archived = False
    if not re.search(r'Page\ 1\ of\ ', topicPage.html):
      raise InvalidTopicError(self)

    if topicPage.authed:
      # hooray, start pulling info.
      self.set(self.parse(topicPage.html))
    else:
      raise connection.UnauthorizedError(self.connection)
    if self._csrfKey != self.connection.topicCSRFKey:
      self.connection.topicCSRFKey = self._csrfKey

  @property
  @base.loadable
  def date(self):
    return self._date
  @date.setter
  def date(self, stamp):
    self._date = stamp

  @property
  @base.loadable
  def title(self):
    return self._title

  @property
  @base.loadable
  def archived(self):
    return self._archived

  @property
  @base.loadable
  def closed(self):
    return self._closed

  @property
  @base.loadable
  def pages(self):
    return self._pages

  @property
  @base.loadable
  def tags(self):
    return self._tags

  @property
  @base.loadable
  def user(self):
    return self._user

  @property
  @base.loadable
  def lastPostTime(self):
    return self._lastPostTime

  def getPagePosts(self, text):
    """
    Takes the HTML of one page of a topic or link and returns a list containing the HTML for one post in each element on said page.
    """
    return text.split('<td class="userpic">')[:-1]

  def appendPosts(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a topic message listing as fed in by pyparallelcurl and appends the posts contained within to the current topic's posts.
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
      else:
        raise connection.UnauthorizedError(self.connection)
      
    # parse this page and append posts to post list.
    thisPagePosts = self.getPagePosts(text)
    for postRow in thisPagePosts:
      newPost = self.connection.post(1, self)
      newPost.set(newPost.parse(postRow))
      if newPost not in self:
        self._postIDs[newPost] = 1
        self._posts.append(newPost)

  def getPosts(self, endPageNum=None, user=None):
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
      
    userID = "" if user is None else user.id

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

  def appendImages(self, html, url, curlHandle, params):
    if not html:
      thisPage = self.connection.page(url)
      raise page.PageLoadError(thisPage)
    
    thisPage = page.Page(self.connection, url)
    thisPage._html = html
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendImages, paramArray)
        return
      else:
        raise connection.UnauthorizedError(self.connection)

    # parse this page and append images to image list.
    for idx,image in enumerate(parse_imagemap(html)):
      newImage = self.connection.image(md5=image['md5'], filename=image['filename'])
      newImage.set({'imagemap_order': (params['page'], idx)})
      self._images.append(newImage)
    return

  def getImages(self, maxPage=None):
    """
      Fetches all images in this topic's map.
    """
    self._images = []
    if maxPage is None:
      # first, get the first page.
      firstPageParams = {
        'topic': self.id,
        'page': 1
      }
      firstPageUrl = 'https://images.endoftheinter.net/imagemap.php?' + urllib.urlencode(firstPageParams)
      firstPage = self.connection.page(firstPageUrl)
      firstPageSoup = bs4.BeautifulSoup(firstPage.html)
      infobar = firstPageSoup.find('div', {'class': 'infobar'})
      if infobar is None:
        # this image doesn't exist.
        raise InvalidTopicError(self)
      numPages = int(infobar.find('span').text)
      # fetch the images on this page.
      self.appendImages(firstPage.html, firstPageUrl, self.connection.parallelCurl, {'page': 1})
      startPage = 2
    else:
      startPage = 1
      numPages =  maxPage

    # now fetch all the pages.
    for page in range(startPage, int(numPages)+1):
      imageMapParams = urllib.urlencode({'topic': self.id, 'page': page})
      self.connection.parallelCurl.startrequest('https://images.endoftheinter.net/imagemap.php?' + imageMapParams, self.appendImages, {'page': page})
    self.connection.parallelCurl.finishallrequests()
    self._images = sorted(self._images, key=lambda x: x._imagemap_order)

  def images(self, maxPage=None):
    if self._images is None:
      self.getImages(maxPage=maxPage)
    return self._images

  def make_post(self, html):
    # get post-key.
    if self.connection.topicCSRFKey is None:
      self.load()
    if isinstance(html, unicode):
      html = html.encode('utf-8')
    post_fields = {
      'topic': self.id,
      'h': self.connection.topicCSRFKey,
      'message': html,
      '-ajaxCounter': 0
    }
    response = self.connection.page('https://boards.endoftheinter.net/async-post.php').post(post_fields)
    if "Message posted." in response:
      return True
    else:
      return False
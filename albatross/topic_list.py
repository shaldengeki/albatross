#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    TopicList - Topic list information retrieval and manipulation.
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
import base

class TopicListError(albatross.Error):
  def __init__(self, topicList, message=None):
    super(TopicListError, self).__init__(message=message)
    self.topicList = topicList
  def __str__(self):
    return "\n".join([
        super(TopicListError, self).__str__()
      ])

class TopicList(base.Base):
  '''
  Topic list-loading object for albatross.
  '''
  def __init__(self, conn, allowedTags=None, forbiddenTags=None):
    super(TopicList, self).__init__(conn)
    self._topics = None
    self._allowedTags = allowedTags
    self._forbiddenTags = forbiddenTags
  def __getitem__(self, index):
    return self.topics[index]
  def __delitem__(self, index):
    del self.topics[index]
  def __setitem__(self, index, value):
    self.topics[index] = value
  def __len__(self):
    return len(self.topics)
  def __iter__(self):
    for topic in self.topics:
      yield topic
  def __contains__(self, topic):
    return any((topic.id == containedTopic.id for containedTopic in self.topics))

  def formatTagQueryString(self):
    """
    Returns a string formatted for ETI's topic search URL using this topic list's properties.
    E.g. "[Posted]-[Anonymous]+[Starcraft]+[Programming]"
    """
    allowed = True and self._allowedTags or []
    forbidden = True and self._forbiddenTags or []
    if len(forbidden) > 0:
      return "-".join(["+".join(["[" + urllib2.quote(tag) + "]" for tag in allowed]), "-".join(["[" + urllib2.quote(tag) + "]" for tag in forbidden])])
    else:
      return "+".join(["[" + urllib2.quote(tag) + "]" for tag in allowed])

  def parse(self, text):
    """
    Returns a dict of topic attributes from a line of a topic list, or throws an exception if it doesn't match a topic listing regex.
    """
    thisTopic = re.search(r'\<td\ class\=\"oh\"\>\<div\ class\=\"fl\"\>((?P<closed><span\ class\=\"closed\"\>))?\<a\ href\=\"//[a-z]+\.endoftheinter\.net/showmessages\.php\?topic\=(?P<topicID>[0-9]+)\">(<b>)?(?P<title>[^<]+)(</b>)?\</a\>(</span>)?</div\>\<div\ class\=\"fr\"\>((?P<tags>(.+?))\ )?\<\/div\></td\>\<td\>(?P<moneybags>\<span\ style\=\"color\:green\;font\-weight\:bold\"\>\$\ \$\<\/span\>)?\ *(\<a\ href\=\"//endoftheinter\.net/profile\.php\?user=(?P<userID>[0-9]+)\"\>(?P<username>[^<]+)\</a\>)?(Human)?\ *(?P<moneybags2>\<span\ style\=\"color\:green\;font\-weight\:bold\"\>\$\ \$\<\/span\>)?\<\/td\>\<td\>(?P<postCount>[0-9]+)(\<span id\=\"u[0-9]+_[0-9]+\"\> \(\<a href\=\"//(boards)?(archives)?\.endoftheinter\.net/showmessages\.php\?topic\=[0-9]+(\&amp\;page\=[0-9]+)?\#m[0-9]+\"\>\+(?P<newPostCount>[0-9]+)\</a\>\)\&nbsp\;\<a href\=\"\#\" onclick\=\"return clearBookmark\([0-9]+\, \$\(\&quot\;u[0-9]+\_[0-9]+\&quot\;\)\)\"\>x\</a\>\</span\>)?\</td\>\<td\>(?P<lastPostTime>[^>]+)\</td\>', text)
    if not thisTopic:
      raise TopicListError(self)
    parser = HTMLParser.HTMLParser()
    if thisTopic.group('userID') and thisTopic.group('username'):
      user = self.connection.user(int(thisTopic.group('userID'))).set({'name': parser.unescape(thisTopic.group('username'))})
    else:
      user = self.connection.user(0).set({'name': 'Human'})
    newPosts = 0
    if thisTopic.group('newPostCount'):
      newPosts = int(thisTopic.group('newPostCount'))
    closedTopic = False
    if thisTopic.group('closed'):
      closedTopic = True
    if thisTopic.group('tags'):
      tags = self.connection.tags(tags=[parser.unescape(re.search(r'\"\>(?P<name>[^<]+)', tag).group('name')) for tag in thisTopic.group('tags').split("</a>") if tag])
    else:
      tags = self.connection.tags(tags=[])
    # If we're searching for just one tag, it won't show in the topic list, so we've got to manually-append it.
    if self._allowedTags and len(self._allowedTags) == 1:
      tags.append(self.connection.tag(self._allowedTags[0]))
    if thisTopic.group('lastPostTime'):
      lastPostTime = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(thisTopic.group('lastPostTime'), "%m/%d/%Y %H:%M"))
    else:
      lastPostTime = False
    return {
      'id': int(thisTopic.group('topicID')),
      'title': parser.unescape(thisTopic.group('title')),
      'user': user,
      'postCount': int(thisTopic.group('postCount')),
      'newPosts': newPosts,
      'lastPostTime': lastPostTime,
      'closed': closedTopic,
      'tags': tags
    }

  def search(self, query="", maxTime=None, maxID=None, activeSince=None, topics=None, recurse=False):
    """
    Searches for topics using given parameters, and returns a list of dicts of returned topics.
    By default, recursively iterates through every page of search results.
    Upon failure returns False.
    """
    if topics is None:
      self._topics = []

    # if allowedTags or forbiddenTags is provided, it overrides this topiclist object's personal allowed or forbidden tags.
    if maxID is None:
      maxID = ""

    if activeSince is None:
      activeSince = pytz.timezone('America/Chicago').localize(datetime.datetime(1970, 1, 1))
    else:
      # the topic listing only provides minute-level resolution, so remove seconds and microseconds from activeSince.
      activeSince = activeSince - datetime.timedelta(0, activeSince.second, activeSince.microsecond)

    while not maxTime or maxTime > activeSince:
      # assemble the search query and request this search page's topic listing.
      requestArgs = {
        'q': unicode(query).encode('utf-8')
      }
      if maxTime is not None:
        if isinstance(maxTime, datetime.datetime):
          maxTime = calendar.timegm(maxTime.utctimetuple())
        requestArgs['ts'] = unicode(maxTime).encode('utf-8')
      if maxID is not None:
        requestArgs['t'] = unicode(maxID).encode('utf-8')
      searchQuery = urllib.urlencode(requestArgs)

      url = 'https://boards.endoftheinter.net/topics/' + self.formatTagQueryString() + '?' + searchQuery
      topicPageHTML = self.connection.page(url).html

      # split the topic listing string into a list so that one topic is in each element.
      topicListingHTML = albatross.getEnclosedString(topicPageHTML, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
      if not topicListingHTML:
        # No topic listing table. this means there are no topics that matched the search.
        break

      topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []
      originalTopicsNum = len(self._topics)
      for topic in topicListingHTML:
        topicInfo = self.parse(topic)
        if topicInfo and topicInfo['lastPostTime'] >= activeSince:
          self._topics.append(self.connection.topic(topicInfo['id']).set(topicInfo))
      
      if len(self._topics) == originalTopicsNum:
        # No matching topics; end our search.
        break

      if not recurse:
        break
      # we can't parallelize this, since we have no way of predicting the next ts and t parameters. DAMN YOU KEYSET PAGING
      maxTime = self._topics[-1].lastPostTime
      maxID = self._topics[-1].id
    self._topics = sorted(self._topics, key=lambda topic: topic.lastPostTime, reverse=True)
    return self

  @property
  def topics(self):
    if self._topics is None:
      self.search()
    return self._topics
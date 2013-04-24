#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    TopicList - Topic list information retrieval and manipulation.
'''
import datetime
import pytz
import re
import urllib
import urllib2

import albatross
from topic import Topic

class TopicListException(Exception):
  pass

class TopicList(object):
  '''
  Topic list-loading object for albatross.
  '''
  def __init__(self, connection):
    self.connection = connection
    self._topics = []
  def __getitem__(self, index):
    return self.topics[index]
  def __len__(self):
    return len(self.topics)

  def formatTagQueryString(self, allowedTags=[], forbiddenTags=[]):
    """
    Takes a list of tag names.
    Returns a string formatted for ETI's topic search URL.
    E.g. "Posted-Anonymous+Starcraft+Programming"
    """
    if len(forbiddenTags) > 0:
      return "-".join(["+".join(allowedTags), "-".join(forbiddenTags)])
    else:
      return "+".join(allowedTags)

  def parse(self, text):
    """
    Returns a dict of topic attributes from a line of a topic list, or throws an exception if it doesn't match a topic listing regex.
    """
    thisTopic = re.search(r'\<td\ class\=\"oh\"\>\<div\ class\=\"fl\"\>((?P<closed><span\ class\=\"closed\"\>))?\<a\ href\=\"//[a-z]+\.endoftheinter\.net/showmessages\.php\?topic\=(?P<topicID>[0-9]+)\">(<b>)?(?P<title>[^<]+)(</b>)?\</a\>(</span>)?</div\>\<div\ class\=\"fr\"\>((?P<tags>(.+?))\ )?\<\/div\></td\>\<td\>(?P<moneybags>\<span\ style\=\"color\:green\;font\-weight\:bold\"\>\$\ \$\<\/span\>)?\ *(\<a\ href\=\"//endoftheinter\.net/profile\.php\?user=(?P<userID>[0-9]+)\"\>(?P<username>[^<]+)\</a\>)?(Human)?\ *(?P<moneybags2>\<span\ style\=\"color\:green\;font\-weight\:bold\"\>\$\ \$\<\/span\>)?\<\/td\>\<td\>(?P<postCount>[0-9]+)(\<span id\=\"u[0-9]+_[0-9]+\"\> \(\<a href\=\"//(boards)?(archives)?\.endoftheinter\.net/showmessages\.php\?topic\=[0-9]+(\&amp\;page\=[0-9]+)?\#m[0-9]+\"\>\+(?P<newPostCount>[0-9]+)\</a\>\)\&nbsp\;\<a href\=\"\#\" onclick\=\"return clearBookmark\([0-9]+\, \$\(\&quot\;u[0-9]+\_[0-9]+\&quot\;\)\)\"\>x\</a\>\</span\>)?\</td\>\<td\>(?P<lastPostTime>[^>]+)\</td\>', text)
    if not thisTopic:
      raise TopicListException(text)
    user = {'userID': 0, 'username': 'Human', 'moneybags': False}
    if thisTopic.group('userID') and thisTopic.group('username'):
      user['userID'] = int(thisTopic.group('userID'))
      user['username'] = thisTopic.group('username')
    if thisTopic.group('moneybags') and thisTopic.group('moneybags2'):
      user['moneybags'] = True
    newPosts = 0
    if thisTopic.group('newPostCount'):
      newPosts = int(thisTopic.group('newPostCount'))
    closedTopic = False
    if thisTopic.group('closed'):
      closedTopic = True
    if thisTopic.group('tags'):
      tags = [re.search(r'\"\>(?P<name>[^<]+)', tag).group('name') for tag in thisTopic.group('tags').split("</a>") if tag]
    else:
      tags = []
    if thisTopic.group('lastPostTime'):
      lastPostTime = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(thisTopic.group('lastPostTime'), "%m/%d/%Y %H:%M"))
    else:
      lastPostTime = False
    return dict([('id', int(thisTopic.group('topicID'))), ('title', thisTopic.group('title')), ('user', {'id': user['userID'], 'name': user['username']}), ('postCount', int(thisTopic.group('postCount'))), ('newPosts', newPosts), ('lastPostTime', lastPostTime), ('closed', closedTopic), ('tags', tags)])

  def search(self, query="", allowedTags=[], forbiddenTags=[], maxTopicTime="", maxTopicID="", topicsActiveSince=False, topics=None, recurse=False):
    """
    Searches for topics using given parameters, and returns a list of dicts of returned topics.
    By default, recursively iterates through every page of search results.
    Upon failure returns False.
    """
    if topics is None:
      self._topics = []
    
    # check to see if we need to request a page.
    if topicsActiveSince and maxTopicTime and maxTopicTime <= topicsActiveSince:
      return self
    
    # assemble the search query and request this search page's topic listing.
    searchQuery = urllib.urlencode([('q', str(query)), ('ts', str(maxTopicTime)), ('t', str(maxTopicID))])
    topicPageHTML = self.connection.page('https://boards.endoftheinter.net/topics/' + self.formatTagQueryString(allowedTags=allowedTags, forbiddenTags=forbiddenTags) + '?' + searchQuery).html
    
    # split the topic listing string into a list so that one topic is in each element.
    topicListingHTML = albatross.getEnclosedString(topicPageHTML, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
    if not topicListingHTML:
      return self
    topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []
    
    originalTopicsNum = len(self._topics)
    for topic in topicListingHTML:
      topicInfo = self.parse(topic)
      if topicInfo and (not topicsActiveSince or topicInfo['lastPostTime'] > topicsActiveSince):
        self._topics.append(Topic(self.connection, topicInfo['id']).set(topicInfo))
    
    if len(self._topics) == originalTopicsNum:
      return self

    if not recurse:
      return self
    # we can't parallelize this, since we have no way of predicting the next ts and t parameters.
    return True and self.search(query=query, maxTopicTime=self._topics[-1]['lastPostTime'], maxTopicID=self._topics[-1]['id'], topicsActiveSince=topicsActiveSince, topics=self._topics, recurse=recurse) or False

  @property
  def topics(self):
    return self._topics
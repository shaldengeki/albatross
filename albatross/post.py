#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Post - Post information retrieval and manipulation.
'''

import datetime
import HTMLParser
import pytz
import re

import albatross
import connection
import base
import topic

class InvalidPostError(topic.InvalidTopicError):
  def __init__(self, post):
    super(InvalidPostError, self).__init__(post.topic)
    self.post = post
  def __str__(self):
    return "\n".join([
      super(InvalidPostError, self).__str__(),
      "PostID: " + unicode(self.post.id),
      ])
class MalformedPostError(InvalidPostError):
  def __init__(self, post, topic, text):
    super(MalformedPostError, self).__init__(post, topic)
    self.text = text
  def __str__(self):
    return "\n".join([
        super(MalformedPostError, self).__str__(),
        "Text: " + unicode(self.text)
      ])

class Post(base.Base):
  '''
  Post-loading object for albatross.
  '''
  def __init__(self, conn, id, topic):
    super(Post, self).__init__(conn)
    self.id = id
    self.topic = topic
    if not isinstance(self.id, int) or int(self.id) < 1:
      raise InvalidPostError(self)
    else:
      self.id = int(self.id)
    self._date = None
    self._user = None
    self._html = None
    self._sig = None

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + unicode(self.id),
      "User: " + unicode(self.user['name']) + " (" + unicode(self.user['id']) + ")",
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p"),
      "Post:",
      unicode(self.html),
      "---",
      unicode(self.sig)
      ])

  def __contains__(self, searchString):
    return searchString in self.html

  def __index__(self):
    return self.id

  def __hash__(self):
    return self.id

  def __eq__(self, post):
    return self.id == post.id

  def parse(self, text):
    """
    Given some HTML containing a post, return a dict of attributes.
    """
    parser = HTMLParser.HTMLParser()
    timeString = albatross.getEnclosedString(text, r'<b>Posted:</b> ', r' \| ', greedy=False)
    altTimeString = albatross.getEnclosedString(text, r'<b>Posted:</b> ', r'</div>', greedy=False)

    timeString = timeString if timeString and len(timeString) < len(altTimeString) else altTimeString

    user = self.connection.user(int(albatross.getEnclosedString(text, r'<b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">'))).set({'name': parser.unescape(True and albatross.getEnclosedString(text, r'<b>From:</b>\ <a href="//endoftheinter\.net/profile\.php\?user=\d+">', r'</a>') or u'Human')})
    attrs = {
      'id': int(albatross.getEnclosedString(text, r'<div class="message-container" id="m', r'">')),
      'user': user,
      'date': pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(timeString, "%m/%d/%Y %I:%M:%S %p")),
      'html': albatross.getEnclosedString(text, r' class="message">', '(\n)?---<br />(\n)?', multiLine=True, greedy=True),
      'sig': albatross.getEnclosedString(text, '(\n)?---<br />(\n)?', r'</td>', multiLine=True, greedy=False)
    }
    if attrs['html'] is False:
      # sigless and on message detail page.
      attrs['html'] = albatross.getEnclosedString(text, r' class="message">', r'</td>', multiLine=True, greedy=False)
      attrs['sig'] = u""
    if attrs['html'] is False:
      # sigless and on topic listing.
      attrs['html'] = albatross.getEnclosedString(text, r' class="message">', r'', multiLine=True, greedy=True)
    if attrs['html'] is False:
      raise MalformedPostError(self, self.topic, unicode(text))
    attrs['html'] = attrs['html'].rstrip("\n")
    if attrs['sig'] is not False:
      attrs['sig'] = attrs['sig'].rstrip("\n")
    return attrs

  def load(self):
    """
    Fetches post info.
    """
    postPage = self.connection.page('https://boards.endoftheinter.net/message.php?id=' + unicode(self.id) + '&topic=' + unicode(self.topic.id))
    # check to see if this page is valid.
    if re.search(r'<em>Invalid topic.</em>', postPage.html) or re.search(r'<em>Can\'t find that post...</em>', postPage.html):
      raise InvalidPostError(self)

    if postPage.authed:
      # hooray, start pulling info.
      self.set(self.parse(postPage.html))
    else:
      raise connection.UnauthorizedError(self.connection)

  @property
  @base.loadable
  def date(self):
    return self._date

  @property
  @base.loadable
  def html(self):
    return self._html

  @property
  @base.loadable
  def user(self):
    return self._user

  @property
  @base.loadable
  def sig(self):
    return self._sig
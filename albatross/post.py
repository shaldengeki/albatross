#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Post - Post information retrieval and manipulation.
'''

import datetime
import pytz
import re

import albatross
import connection
import topic

class InvalidPostError(topic.InvalidTopicError):
  def __init__(self, post):
    super(InvalidPostError, self).__init__(post.topic)
    self.post = post
  def __str__(self):
    return "\n".join([
      super(InvalidPostError, self).__str__(),
      "PostID: " + str(self.post.id),
      ])
class MalformedPostError(InvalidPostError):
  def __init__(self, post, topic, text):
    super(MalformedPostError, self).__init__(post, topic)
    self.text = text
  def __str__(self):
    return "\n".join([
        super(MalformedTagError, self).__str__(),
        "Text: " + str(self.text)
      ])

class Post(object):
  '''
  Post-loading object for albatross.
  '''
  def __init__(self, conn, id, topic):
    self.connection = conn
    self.id = int(id)
    self.topic = topic
    self._date = None
    self._user = None
    self._html = None
    self._sig = None

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + str(self.id),
      "User: " + unicode(self.user['name']) + " (" + str(self.user['id']) + ")",
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p"),
      "Post:",
      unicode(self.html),
      "---",
      unicode(self.sig)
      ])

  def set(self, attrDict):
    """
    Sets attributes of this post object with keys found in dict.
    """
    for key in attrDict:
      if key == "id":
        self.id = int(attrDict["id"])
      else:
        setattr(self, "_" + key, attrDict[key])
    return self

  def parse(self, text):
    """
    Given some HTML containing a post, return a dict.
    """
    timeString = albatross.getEnclosedString(text, r'<b>Posted:</b> ', r' \| ')
    if not timeString:
      timeString = albatross.getEnclosedString(text, r'<b>Posted:</b> ', r'</div>')
    postDict = {'id': int(albatross.getEnclosedString(text, r'<div class="message-container" id="m', r'">')), 'user': {'name': albatross.getEnclosedString(text, r'<b>From:</b>\ <a href="//endoftheinter\.net/profile\.php\?user=\d+">', r'</a>'), 'id': int(albatross.getEnclosedString(text, r'<b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">'))}, 'date': pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(timeString, "%m/%d/%Y %I:%M:%S %p")), 'html': albatross.getEnclosedString(text, r' class="message">', r'---<br />', multiLine=True, greedy=True), 'sig': albatross.getEnclosedString(text, r'---<br />\n', r'</td>', multiLine=True, greedy=False)}
    if postDict['html'] is False:
      postDict['html'] = albatross.getEnclosedString(text, r' class="message">', r'', multiLine=True, greedy=True)
      postDict['sig'] = ""
    if postDict['html'] is False:
      raise MalformedPostError(self, self.topic, str(text))
    return postDict

  def load(self):
    """
    Fetches post info.
    """
    postPage = self.connection.page('https://boards.endoftheinter.net/message.php?id=' + str(self.id) + '&topic=' + str(self.topic.id))
    # check to see if this page is valid.
    if re.search(r'<em>Invalid topic.</em>', postPage.html) or re.search(r'<em>Can\'t find that post...</em>', postPage.html):
      raise InvalidPostError(self)

    if postPage.authed:
      # hooray, start pulling info.
      self.set(self.parse(postPage.html))
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
  def html(self):
    if self._html is None:
      self.load()
    return self._html

  @property
  def user(self):
    if self._user is None:
      self.load()
    return self._user

  @property
  def sig(self):
    if self._sig is None:
      self.load()
    return self._sig
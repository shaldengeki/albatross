#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Post - Post information retrieval and manipulation.
'''

import bs4
import datetime
import HTMLParser
import pytz
import re

import albatross
import connection
import base
import topic
import post_nodes
import image

class InvalidPostError(topic.InvalidTopicError):
  def __init__(self, post, topic=None, message=None):
    super(InvalidPostError, self).__init__(post.topic, message=message)
    self.post = post
    self.topic = topic

  def __str__(self):
    return "\n".join([
      super(InvalidPostError, self).__str__(),
      "ID: " + unicode(self.post.id),
      "Topic ID: " + ( unicode(self.topic.id) if topic else u"None" )
    ])
class MalformedPostError(InvalidPostError):
  def __init__(self, post, topic, text, message=None):
    super(MalformedPostError, self).__init__(post, topic, message=message)
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
  def __init__(self, conn, id, topic, **kwargs):
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
    self._nodes = None
    self._images = None
    self._sig = None

    self.set(kwargs)

  def __str__(self):
    if self._date is None:
      self.load()
    return "\n".join([
      "ID: " + unicode(self.id),
      "User: " + unicode(self.user.name) + " (" + unicode(self.user.id) + ")",
      "Date: " + self.date.strftime("%m/%d/%Y %I:%M:%S %p"),
      "Post:",
      unicode(self.html),
      "---",
      unicode(self.sig)
      ])

  def __contains__(self, searchItem):
    if isinstance(searchItem, image.Image):
      return searchItem in self.images
    elif isinstance(searchItem, Post):
      return searchItem in self.quotes
    else:
      return searchItem in self.html

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
    dom = bs4.BeautifulSoup(text)
    container = dom.find('div', {'class': 'message-container'})
    if not container:
      raise MalformedPostError(self, self.topic, text, message="Could not find message container.")
    post_id = int(container.get('id')[1:])

    message_top = container.find('div', {'class': 'message-top'})
    if not message_top:
      raise MalformedPostError(self, self.topic, text, message="Could not find message message top.")

    date_posted = message_top.find(text='Posted:').next_element[1:-3]
    user_link = message_top.find('a')
    if user_link.get('href').startswith('//endoftheinter.net/profile.php'):
      user_id = int(re.search('user=(?P<id>[0-9]+)', user_link.get('href')).group('id'))
      user_name = user_link.text
    else:
      # No user profile link; this is a post on HA.
      user_id = 0
      user_name = u'Human'

    attrs = {
      'id': post_id,
      'user': self.connection.user(user_id).set({'name': user_name}),
      'date': pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(date_posted, "%m/%d/%Y %I:%M:%S %p")),
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
      raise MalformedPostError(self, self.topic, text)
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

    if not postPage.authed:
      raise connection.UnauthorizedError(self.connection)
    # hooray, start pulling info.
    self.set(self.parse(postPage.html))
    dom = bs4.BeautifulSoup(postPage.html)
    container = dom.find('td', {'class': 'message'})
    self.set({'nodes': post_nodes.get_child_nodes(self.connection, unicode(container))})

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

  @property
  @base.loadable
  def nodes(self):
    return self._nodes

  @property
  def images(self):
    return [image for container in map(lambda x: x.images, filter(lambda x: isinstance(x, post_nodes.ImageContainerNode), self.nodes)) for image in container]

  @property
  def quotes(self):
    return filter(lambda x: isinstance(x, post_nodes.QuoteNode), self.nodes)
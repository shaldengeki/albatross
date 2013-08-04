#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    TagList - Tag list information retrieval and manipulation.
'''
import HTMLParser
import urllib

import albatross
import page
import tag

class TagListError(albatross.Error):
  pass

class TagList(object):
  '''
  Tag list-loading object for albatross.
  '''
  def __init__(self, conn, tags=None, active=False):
    self.connection = conn
    if tags is None:
      tags = []
    self._tagNames = dict(zip(tags, [1]*len(tags)))
    self._tags = None
    if active:
      parser = HTMLParser.HTMLParser()
      mainPage = page.Page(self.connection, "https://endoftheinter.net/main.php")
      tagLinksHTML = albatross.getEnclosedString(mainPage.html, r'<div style="font-size: 14px">', r'</div>', multiLine=True)
      tagLinks = tagLinksHTML.split('&nbsp;&bull; ')
      for text in tagLinks:
        self._tagNames[parser.unescape(albatross.getEnclosedString(text, '">', '</a>')).strip()] = 1
      self.load()
  def __getitem__(self, index):
    return self.tags[index]
  def __delitem__(self, index):
    del self.tags[index]
  def __setitem__(self, index, value):
    self.tags[index] = value
  def __len__(self):
    return len(self.tags)
  def __iter__(self):
    for tagObj in self.tags:
      yield tagObj
  def __contains__(self, tag):
    return tag.name in self._tagNames
  def __reversed__(self):
    return self.tags[::-1]

  def appendTag(self, text, url, curlHandle, tagList):
    """
    Takes the HTML of ETI's ajax tag interface and parses info from it.
    Appends the resultant tag array to the tag list.
    """
    thisPage = page.Page(self.connection, url)
    thisPage._html = text
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendTag)
        return
    # parse the text given into a tag object to append to tagList.
    thisTag = self.connection.tag("")
    try:
      thisTag.set(thisTag.parse(text))
    except tag.InvalidTagError:
      # workaround for tags where extended information doesn't display properly.
      if "e=" not in url:
        raise
      self.connection.parallelCurl.startrequest(url.replace("e=&", ""), self.appendTag)
      return

    if thisTag and thisTag.name not in self._tagNames:
      if self._tags is None:
        self._tags = []
      self._tagNames[thisTag.name] = 1
      self._tags.append(thisTag)

  def load(self):
    """
    Resets self._tags with naive tag objects.
    """
    self._tags = []
    if self._tagNames:
      self._tags = [self.connection.tag(tagName) for tagName in self._tagNames]

  @property
  def tags(self):
    if self._tags is None:
      self.load()
    return self._tags

  def append(self, appTag):
    if appTag not in self:
      self._tagNames[appTag.name] = 1
      if isinstance(self._tags, list):
        self._tags.append(appTag)
    return self

  def topics(self):
    return self.connection.topics(allowedTags=self._tagNames.keys())
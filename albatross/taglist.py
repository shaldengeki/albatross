#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    TagList - Tag list information retrieval and manipulation.
'''
import urllib

import albatross
import page
import tag

class TagListException(Exception):
  pass

class TagList(object):
  '''
  Tag list-loading object for albatross.
  '''
  def __init__(self, connection, tags=None, active=False):
    self.connection = connection
    self._tagNames = tags
    self._tags = None
    if active and tags is None:
      mainPage = page.Page(self.connection, "https://endoftheinter.net/main.php")
      tagLinksHTML = albatross.getEnclosedString(mainPage.html, '<div style\="font\-size\: 14px">', '</div>', multiLine=True)
      tagLinks = tagLinksHTML.split('&nbsp;&bull; ')
      self._tagNames = [albatross.getEnclosedString(text, '">', '</a>').strip() for text in tagLinks]
  def __getitem__(self, index):
    return self.tags[index]
  def __len__(self):
    return len(self.tags)

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
    thisTag = tag.Tag(self.connection, "")
    try:
      thisTag.set(thisTag.parse(text))
    except tag.InvalidTagException:
      # workaround for tags where extended information doesn't display properly.
      if "e=" not in url:
        raise
      self.connection.parallelCurl.startrequest(url.replace("e=&", ""), self.appendTag)
      return

    if thisTag:
      self._tags.append(thisTag)

  def load(self):
    """
    Returns all the information that the currently signed-in user can view about the tag(s).
    """
    if not self._tags:
      self._tags = []

    for name in self._tagNames:
      tagInfoParams = urllib.urlencode([('e', ''), ('q', str(name).replace(" ", "_")), ('n', '1')])
      self.connection.parallelCurl.startrequest("https://boards.endoftheinter.net/async-tag-query.php?" + tagInfoParams, self.appendTag)
    self.connection.parallelCurl.finishallrequests()

  @property
  def tags(self):
    if self._tags is None:
      self.load()
    return self._tags
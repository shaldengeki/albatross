#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Tag - Tag information retrieval and manipulation.
'''

import json
import sys
import urllib

import albatross
import connection
import page

class InvalidTagError(albatross.Error):
  def __init__(self, tag):
    super(InvalidTagError, self).__init__()
    self.tag = tag
  def __str__(self):
    return "\n".join([
        str(super(InvalidTagError, self)),
        "Name: " + str(self.name)
      ])

class MalformedTagError(InvalidTagError):
  def __init__(self, tag, text):
    super(MalformedTagError, self).__init__(tag)
    self.text = text
  def __str__(self):
    return "\n".join([
        str(super(MalformedTagError, self)),
        "Text: " + str(self.text)
      ])

class Tag(object):
  '''
  Tag-loading object for albatross.
  '''
  def __init__(self, conn, name):
    self.connection = conn
    self.name = name
    self._staff = None
    self._description = None
    self._related = None
    self._forbidden = None
    self._dependent = None

  def set(self, attrDict):
    """
    Sets attributes of this tag object with keys found in dict.
    """
    for key in attrDict:
      if key == "name":
        self.name = attrDict["name"]
      else:
        setattr(self, "_" + key, attrDict[key])
    return self

  def parse(self, text):
    """
    Given some JSON containing a tag, return a dict.
    """
    text = text[1:]
    try:
      tagJSON = json.loads(text)
    except ValueError:
      print "Warning: invalid JSON object provided by ETI ajax tag interface."
      raise MalformedTagError(self, str(tagJSON))
    if len(tagJSON) < 1:
      raise MalformedTagError(self, str(tagJSON))
    tagJSON = tagJSON[0]
    tag = {'name': tagJSON[0]}

    tag['staff'] = []

    moderatorText = albatross.getEnclosedString(tagJSON[1][0], r"<b>Moderators: </b>", r"<br /><b>Administrators:")
    if moderatorText:
      descriptionEndTag = "<br /><b>Moderators:"
      moderatorTags = moderatorText.split(", ")
      for moderator in moderatorTags:
        tag['staff'].append({'name': str(albatross.getEnclosedString(moderator, r'">', r"</a>")), 'id': int(albatross.getEnclosedString(moderator, r"\?user=", r'">')), 'role':'moderator'})
    else:
      descriptionEndTag = "<br /><b>Administrators:"

    administratorText = albatross.getEnclosedString(tagJSON[1][0], startString="<br /><b>Administrators: </b>", greedy=True)
    if administratorText:
      administratorTags = administratorText.split(", ")
      for administrator in administratorTags:
        tag['staff'].append({'name': str(albatross.getEnclosedString(administrator, r'">', r"</a>")), 'id': int(albatross.getEnclosedString(administrator, r"\?user=", r'">')), 'role':'administrator'})
    descriptionText = albatross.getEnclosedString(tagJSON[1][0], r":</b> ", descriptionEndTag)
    if descriptionText:
      tag['description'] = descriptionText
    else:
      tag['description'] = ''

    tagInteractions = tagJSON[1][1]
    tag['related'] = tag['forbidden'] = tag['dependent'] = []
    if len(tagInteractions) > 0:
      if '0' in tagInteractions:
        tag['forbidden'] = [Tag(self.connection, key) for key in tagInteractions['0'].keys()]
      if '1' in tagInteractions:
        tag['dependent'] = [Tag(self.connection, key) for key in tagInteractions['1'].keys()]
      if '2' in tagInteractions:
        tag['related'] = [Tag(self.connection, key) for key in tagInteractions['2'].keys()]
    return tag

  def load(self):
    """
    Fetches tag info.
    """
    tagInfoParams = urllib.urlencode([('e', ''), ('q', str(self.name).replace(" ", "_")), ('n', '1')])
    tagURL = "https://boards.endoftheinter.net/async-tag-query.php?" + tagInfoParams
    tagPage = self.connection.page(tagURL)
    # check to see if this page is valid.
    if tagPage.authed:
      # hooray, start pulling info.
      self.set(self.parse(tagPage.html))
    else:
      raise connection.UnauthorizedError(self.connection)

  @property
  def staff(self):
    if self._staff is None:
      self.load()
    return self._staff

  @property
  def description(self):
    if self._description is None:
      self.load()
    return self._description

  @property
  def related(self):
    if self._related is None:
      self.load()
    return self._related

  @property
  def forbidden(self):
    if self._forbidden is None:
      self.load()
    return self._forbidden

  @property
  def dependent(self):
    if self._dependent is None:
      self.load()
    return self._dependent
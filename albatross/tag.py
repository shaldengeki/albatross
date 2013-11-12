#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Tag - Tag information retrieval and manipulation.
'''

import json
import HTMLParser
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
        super(InvalidTagError, self).__str__(),
        "Name: " + unicode(self.tag.name)
      ])

class MalformedTagError(InvalidTagError):
  def __init__(self, tag, text):
    super(MalformedTagError, self).__init__(tag)
    self.text = text
  def __str__(self):
    return "\n".join([
        super(MalformedTagError, self).__str__(),
        "Text: " + unicode(self.text)
      ])

class Tag(object):
  '''
  Tag-loading object for albatross.
  '''
  def __init__(self, conn, name):
    self.connection = conn
    self.name = unicode(name)
    self._staff = None
    self._description = None
    self._related = None
    self._forbidden = None
    self._dependent = None

  def __str__(self):
    return "\n".join([
      "Tag: " + unicode(self.name),
      "-"*(len(self.name) + 5),
      unicode(self.description),
      "Staff:",
      "------",
      "\n".join([staff['name'] + ": " + staff['role'] for staff in self.staff]),
      "Related tags: " + ", ".join([tag.name for tag in self.related]),
      "Forbidden tags: " + ", ".join([tag.name for tag in self.forbidden]),
      "Dependent tags: " + ", ".join([tag.name for tag in self.dependent])
      ])

  def __index__(self):
    return hash(self.name)

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, tag):
    return self.name == tag.name

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
    Given some JSON containing a tag, return a dict of attributes.
    """
    parser = HTMLParser.HTMLParser()
    text = text[1:]
    try:
      tagJSON = json.loads(text)
    except ValueError:
      print "Warning: invalid JSON object provided by ETI ajax tag interface."
      raise MalformedTagError(self, unicode(text))
    if len(tagJSON) < 1:
      raise MalformedTagError(self, unicode(tagJSON))
    tagJSON = tagJSON[0]
    name = tagJSON[0]
    if name.startswith("["):
      name = name[1:]
    if name.endswith("]"):
      name = name[:-1]
    tag = {'name': name}

    tag['staff'] = []

    moderatorText = albatross.getEnclosedString(tagJSON[1][0], r"<b>Moderators: </b>", r"<br /><b>Administrators:")
    if moderatorText:
      descriptionEndTag = "<br /><b>Moderators:"
      moderatorTags = moderatorText.split(", ")
      for moderator in moderatorTags:
        user = self.connection.user(int(albatross.getEnclosedString(moderator, r"\?user=", r'">'))).set({'name': albatross.getEnclosedString(moderator, r'">', r"</a>")})
        tag['staff'].append({'user': user, 'role':'moderator'})
    else:
      descriptionEndTag = "<br /><b>Administrators:"

    administratorText = albatross.getEnclosedString(tagJSON[1][0], startString="<br /><b>Administrators: </b>", greedy=True)
    if administratorText:
      administratorTags = administratorText.split(", ")
      for administrator in administratorTags:
        user = self.connection.user(int(albatross.getEnclosedString(administrator, r"\?user=", r'">'))).set({'name': albatross.getEnclosedString(administrator, r'">', r"</a>")})
        tag['staff'].append({'user': user, 'role':'administrator'})
    descriptionText = albatross.getEnclosedString(tagJSON[1][0], r":</b> ", descriptionEndTag)
    if descriptionText:
      tag['description'] = parser.unescape(descriptionText)
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
    tagInfoParams = urllib.urlencode([('e', ''), ('q', unicode(self.name).encode('utf-8')), ('n', '1')])
    tagURL = "https://boards.endoftheinter.net/async-tag-query.php?" + tagInfoParams
    tagPage = self.connection.page(tagURL)
    # check to see if this page is valid.
    if tagPage.authed:
      # hooray, start pulling info.
      try:
        self.set(self.parse(tagPage.html))
      except MalformedTagError, e:
        e.message = "URL: " + unicode(tagURL)
        raise e
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

  def topics(self):
    return self.connection.topics(allowedTags=[self.name])
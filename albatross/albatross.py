#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl
'''

import re

SITE_MAIN = {"url":"https://endoftheinter.net/","fields":{"username":"b","password":"p"}}
SITE_MOBILE = {"url":"https://iphone.endoftheinter.net/","fields":{"username":"username","password":"password"}}

class Error(Exception):
  def __init__(self, message=None):
    super(Error, self).__init__()
    self.message = message
  def __str__(self):
    return unicode(self.message) if self.message is not None else u""

def getEnclosedString(text, startString='', endString='', multiLine=False, greedy=False):
  """
  Given some text and two strings, return the (unicode) string that is encapsulated by the first sequence of these two strings in order.
  If either string is not found or text is empty, return false.
  Multiline option makes the return possibly multi-line.
  """
  if not text or not len(text):
    return False
  flags = re.DOTALL if multiLine else False

  # Default to non-greedy UNLESS greedy is provided or end string is empty (user is looking for everything past a certain point)
  greedyPart = "" if greedy or endString == '' else "?"
  startString = "^.*?" if startString == '' else startString
  endString = ".*?$" if endString == '' else endString
  stringMatch = re.search(unicode(startString) + (r"(?P<return>.*%s)" % greedyPart) + unicode(endString), text, flags=flags)
  if not stringMatch or stringMatch.group('return') is None:
    return False
  if isinstance(stringMatch.group('return'), unicode):
    return stringMatch.group('return')
  else:
    return unicode(stringMatch.group('return'), encoding='latin-1')
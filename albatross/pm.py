#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    PM - Private message information retrieval and manipulation.
'''

import bs4
import urllib
import datetime
import pytz

import albatross
import page
import post

from pm_thread import InvalidPMThreadError
class UnloadedPMError(InvalidPMThreadError):
  def __init__(self, pm):
    super(UnloadedPMError, self).__init__(pm.thread)
    self.pm = pm
  def __str__(self):
    return "\n".join([
      super(UnloadedPMError, self).__str__(),
      "ID: " + unicode(self.pm.id),
    ])

class InvalidPMSubjectError(albatross.Error):
  def __init__(self, subject):
    super(InvalidPMSubjectError, self).__init__()
    self.subject = subject
  def __str__(self):
    return "\n".join([
      super(InvalidPMSubjectError, self).__str__(),
      "Subject: " + self.subject
    ])

class InvalidPMMessageError(albatross.Error):
  def __init__(self, message):
    super(InvalidPMMessageError, self).__init__()
    self.message = message
  def __str__(self):
    return "\n".join([
      super(InvalidPMMessageError, self).__str__(),
      "Message: " + self.message
    ])

class CouldNotSendPMError(albatross.Error):
  def __init__(self, user, html):
    super(CouldNotSendPMError, self).__init__()
    self.user = user
    self.html = html
  def __str__(self):
    return "\n".join([
      super(CouldNotSendPMError, self).__str__(),
      "ID: " + unicode(self.user.id),
      "HTML: " + self.html
    ])

def parse_pm(conn, html):
  """
  Given a connection and some html containing a PM's contents,
  return a dict, containing attributes of the PM.
  """
  soup = bs4.BeautifulSoup(html)
  pmInfo = soup.find('div', {'class': 'message-top'})
  user_id = int(albatross.getEnclosedString(pmInfo.find('a').get('href'), 'user=', ''))
  user_name = pmInfo.find('a').text
  posted_elt = pmInfo.find('b', text='Posted:')
  posted_date = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(posted_elt.next_sibling.strip(), "%m/%d/%Y %I:%M:%S %p |"))
  quote_elt = pmInfo.find('a', text='Quote')
  pm_id = int(albatross.getEnclosedString(quote_elt.get('href'), 'quote=', ''))
  pm_thread_id = int(albatross.getEnclosedString(quote_elt.get('href'), 'pm=', '&quote='))
  pmContents = soup.find('table', {'class': 'message-body'}).find('td', {'class': 'message'}).contents
  separators = [i for i, j in enumerate(pmContents) if j == u'\n---']
  if separators:
    lastSeparator = separators[-1]
    pm_html = ''.join(unicode(x) for x in pmContents[:lastSeparator])
    if lastSeparator+2 > len(pmContents):
      pm_sig = ''.join(unicode(x) for x in pmContents[lastSeparator+1:])
    else:
      pm_sig = ''.join(unicode(x) for x in pmContents[lastSeparator+2:])
  else:
    pm_html = ''.join(unicode(x) for x in pmContents)
    pm_sig = ''
    lastSeparator = len(separators)
  return {
    'id': pm_id,
    'user': conn.user(user_id, name=user_name),
    'date': posted_date,
    'thread': conn.pmThread(pm_thread_id),
    'html': pm_html,
    'sig': pm_sig
  }

class PM(post.Post):
  '''
  PM-loading object for albatross.
  '''

  def load(self):
    raise UnloadedPMError(self)

  def parse(self, text):
    return parse_pm(self.connection, text)

  def set(self, attrDict):
    """
    Sets attributes of this PM object with keys found in dict.
    """
    super(PM, self).set(attrDict)
    if hasattr(self, '_thread'):
      self.topic = self._thread
      del self._thread
    return self

  @property
  def thread(self):
    return self._topic
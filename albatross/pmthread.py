#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    PMThread - Private message inbox information retrieval and manipulation.
'''

import bs4
import json
import urllib
import datetime
import pytz

import albatross
import page
import base

class InvalidPMThreadError(albatross.Error):
  def __init__(self, thread):
    super(InvalidPMThreadError, self).__init__()
    self.thread = thread
  def __str__(self):
    return "\n".join([
        super(InvalidPMThreadError, self).__str__(),
        "ID: " + unicode(self.thread.id)
      ])

class InvalidCSRFKeyError(albatross.Error):
  def __init__(self, html, thread=None, user=None):
    super(InvalidCSRFKeyError, self).__init__()
    self.html = html
    self.thread = thread
    self.user = None    
  def __str__(self):
    return "\n".join([
      super(InvalidCSRFKeyError, self).__str__(),
      "HTML: " + self.html,
      "Thread: " + unicode(self.thread),
      "User: " + unicode(self.user)
    ])

class MalformedPMThreadError(albatross.Error):
  def __init__(self, thread, html):
    super(MalformedPMThreadError, self).__init__()
    self.thread = thread
    self.html = html
  def __str__(self):
    return "\n".join([
        super(MalformedPMThreadError, self).__str__(),
        "ID: " + unicode(self.thread.id),
        "HTML: " + self.html
      ])

from pm import parse_pm
def parse_pms(conn, html):
  """
  Given a connection and some html containing a PM thread's contents,
  return a list of dicts, each containing attributes of a PM in the thread.
  """
  pms = []
  soup = bs4.BeautifulSoup(html)
  pmRows = soup.find_all('div', {'class': 'message-container'})
  for pmRow in pmRows:
    pmInfo = parse_pm(conn, unicode(pmRow))
    pms.append(pmInfo)
  return pms

from pm import InvalidPMMessageError
class PMThread(base.Base):
  '''
  Private message thread-loading object for albatross.
  '''
  def __init__(self, conn, id, **kwargs):
    super(PMThread, self).__init__(conn)
    self.id = int(id)
    self._subject = None
    self._pmCount = None
    self._lastPMTime = None
    self._read = None
    self._user = None
    self._pms = None
    self.page = 1
    self._pages = None
    self._csrfKey = None
    self.set(kwargs)

  def __str__(self):
    return "\n".join([
      "ID: " + unicode(self.id),
      "Subject: " + self.subject,
      "Page: " + unicode(self.page) + "/" + unicode(self.pages),
      "PMs:" + unicode(self.pmCount),
      "Date: " + self.lastPMTime.strftime("%m/%d/%Y %I:%M:%S %p")
    ])

  def __len__(self):
    return len(self.pms())

  def __getitem__(self, key):
    return self.pms()[key]

  def __setitem__(self, key, value):
    self.pms()[key] = value

  def __iter__(self):
    for pm in self.pms():
      yield pm

  def __index__(self):
    return self.id

  def __hash__(self):
    return self.id

  def __eq__(self, thread):
    return self.id == thread.id

  def set(self, attrDict):
    """
    Sets attributes of this PM thread object with keys found in dict.
    """
    super(PMThread, self).set(attrDict)
    if hasattr(self, '_page'):
      self.page = self._page
      del self._page
    return self

  def appendPMs(self, html, url, curlHandle, params):
    """
      Given the html of a PM listing of PMs within the current PM thread
      append the PMs on this page to the current thread's PMs.
    """
    if not html:
      thisPage = self.connection.page(url)
      raise page.PageLoadError(thisPage)
    
    thisPage = page.Page(self.connection, url)
    thisPage._html = html
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendPosts, paramArray)
        return
      else:
        raise connection.UnauthorizedError(self.connection)

    # parse this page and append PMs to topic list.
    for idx,pm in enumerate(parse_pms(self.connection, html)):
      pm_id = pm['id']
      thread = pm['thread']
      del pm['id']
      del pm['thread']
      newPM = self.connection.pm(pm_id, thread, **pm)
      newPM.set({'pm_order': (params['page'], idx)})
      self._pms.append(newPM)

  def getPMs(self, maxPage=None):
    """
      Fetches all PMs within this thread.
    """
    self._pms = []
    self._read = True
    if maxPage is None:
      # first, get the first page.
      firstPageParams = {
        'thread': self.id,
        'page': 1
      }
      firstPageUrl = 'https://endoftheinter.net/inboxthread.php?' + urllib.urlencode(firstPageParams)
      firstPage = self.connection.page(firstPageUrl)
      firstPageSoup = bs4.BeautifulSoup(firstPage.html)
      infobar = firstPageSoup.find('div', {'class': 'infobar'})
      if infobar is None:
        # this thread doesn't exist.
        raise InvalidPMThreadError(self)
      numPages = int(infobar.find('span').text)
      # fetch the PMs on this page.
      self.appendPMs(firstPage.html, firstPageUrl, self.connection.parallelCurl, {'page': 1})
      startPage = 2
    else:
      startPage = 1
      numPages = maxPage

    # now fetch all the pages.
    for page in range(startPage, int(numPages)+1):
      threadPageParams = urllib.urlencode({'thread': self.id, 'page': page})
      self.connection.parallelCurl.startrequest('https://endoftheinter.net/inboxthread.php?' + threadPageParams, self.appendPMs, {'page': page})
    self.connection.parallelCurl.finishallrequests()
    self._pms = sorted(self._pms, key=lambda x: x._pm_order)

  def pms(self, maxPage=None):
    """
      Returns a list of PMs within this thread.
    """
    if self._pms is None:
      self.getPMs(maxPage=maxPage)
    return self._pms

  @property
  def subject(self):
    return self._subject

  @property
  def pmCount(self):
    return self._pmCount

  @property
  def lastPMTime(self):
    return self._lastPMTime

  @property
  def read(self):
    return self._read

  @property
  def user(self):
    return self._user

  @property
  def pages(self):
    return self._pages

  @property
  def csrfKey(self):
    return self._csrfKey

  def send_pm(self, message):
    # make sure inputs line up.
    if len(message) < 5 or len(message) > 10240:
      raise InvalidPMMessageError(self, message)
    # get csrf key.
    if self._csrfKey is None:
      threadPage = self.connection.page('https://endoftheinter.net/inboxthread.php?thread=' + unicode(self.id))
      soup = bs4.BeautifulSoup(threadPage.html)
      csrfTag = soup.find("input", {"name": "h"})
      if not csrfTag:
        raise InvalidCSRFKeyError(soup, thread=self)
      self.set({'csrfKey': csrfTag.get('value')})
    if isinstance(message, unicode):
      message = message.encode('utf-8')
    post_fields = {
      'pm': self.id,
      'h': self._csrfKey,
      'message': message,
      '-ajaxCounter': '1'
    }
    try:
      response = self.connection.page('http://endoftheinter.net/async-post.php').post(post_fields)
    except page.PageLoadError:
      # invalid CSRF key.
      raise InvalidCSRFKeyError(html, thread=self)
    try:
      response_obj = json.loads(response[1:])
      if 'success' in response_obj:
        return True
    except ValueError:
      # Invalid parameters.
      if 'You are not authorized to view messages on this board.' in response:
        raise InvalidPMThreadError(self)
      elif 'Your message must be at least' in response:
        raise InvalidPMMessageError(self, message)
    return False
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    PMInbox - Private message inbox information retrieval and manipulation.
'''

import bs4
import urllib
import datetime
import pytz

import albatross
import page
import base

def parse_pm_listing(conn, html):
  """
  Given a connection and some html containing a PM inbox's contents,
  return a list of dicts, each containing attributes of a thread in the inbox.
  """
  threads = []
  soup = bs4.BeautifulSoup(html)
  pmTable = soup.find('table', {'class': 'grid'})
  # first row is header row.
  for row in pmTable.find_all('tr')[1:]:
    rowSections = row.find_all('td')
    pmProps = {
      'read': False,
      'unreadCount': 0
    }
    if rowSections[0].find('b') is None:
      pmProps['read'] = True
    pmProps['subject'] = rowSections[0].find('a').text
    pmProps['id'] = int(albatross.getEnclosedString(rowSections[0].find('a').get('href'), 'thread=', ''))
    user_id = int(albatross.getEnclosedString(rowSections[1].find('a').get('href'), 'user=', ''))
    user_name = rowSections[1].find('a').text
    pmProps['user'] = conn.user(user_id, name=user_name)
    unreadNode = rowSections[2].find('a')
    if unreadNode is not None:
      pmProps['unreadCount'] = int(unreadNode.text[1:])
      unreadNode.extract()
    pmProps['pmCount'] = int(rowSections[2].text.replace(' ()', ''))
    pmProps['lastPMTime'] = pytz.timezone('America/Chicago').localize(datetime.datetime.strptime(rowSections[3].text, "%m/%d/%Y %H:%M"))
    threads.append(pmProps)
  return threads

class PMInbox(base.Base):
  '''
  Private message inbox-loading object for albatross.
  '''
  def __init__(self, conn):
    super(PMInbox, self).__init__(conn)
    self._threads = None

  def __str__(self):
    return "\n".join([
      "User ID: " + unicode(self.conn.user_id)
      ])

  def __len__(self):
    return len(self.threads())

  def __getitem__(self, key):
    return self.threads()[key]

  def __setitem__(self, key, value):
    self.threads()[key] = value

  def __iter__(self):
    for thread in self.threads():
      yield thread

  def appendThreads(self, html, url, curlHandle, params):
    if not html:
      thisPage = self.connection.page(url)
      raise page.PageLoadError(thisPage)
    
    thisPage = page.Page(self.connection, url)
    thisPage._html = html
    if not thisPage.authed:
      if self.connection.reauthenticate():
        self.connection.parallelCurl.startrequest(url, self.appendThreads, paramArray)
        return
      else:
        raise connection.UnauthorizedError(self.connection)

    # parse this page and append PMs to PM list.
    for idx,thread in enumerate(parse_pm_listing(self.connection, html)):
      newThread = self.connection.pmThread(**thread)
      newThread.set({'pm_thread_order': (params['page'], idx)})
      self._threads.append(newThread)
    return

  def getThreads(self, maxPage=None):
    """
      Fetches all PM threads in this user's PM inbox.
    """
    self._threads = []
    if maxPage is None:
      # first, get the first page.
      firstPageParams = {
        'page': 1
      }
      firstPageUrl = 'https://endoftheinter.net/inbox.php?' + urllib.urlencode(firstPageParams)
      firstPage = self.connection.page(firstPageUrl)
      firstPageSoup = bs4.BeautifulSoup(firstPage.html)

      infobar = firstPageSoup.find('div', {'class': 'infobar'})
      numPages = int(infobar.find('span').text)
      # fetch the PMs on this page.
      self.appendThreads(firstPage.html, firstPageUrl, self.connection.parallelCurl, {'page': 1})
      startPage = 2
    else:
      startPage = 1
      numPages =  maxPage

    # now fetch all the pages.
    for page in range(startPage, int(numPages)+1):
      inboxParams = urllib.urlencode({'page': page})
      self.connection.parallelCurl.startrequest('https://endoftheinter.net/inbox.php?' + inboxParams, self.appendThreads, {'page': page})
    self.connection.parallelCurl.finishallrequests()
    self._threads = sorted(self._threads, key=lambda x: x._pm_thread_order)

  def threads(self, page=None, maxPage=None):
    if self._threads is None:
      self.getThreads(maxPage=maxPage)
    if page is not None:
      return self._threads[((page-1)*50):(page*50)]
    return self._threads
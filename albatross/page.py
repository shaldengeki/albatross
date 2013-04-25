#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Page - lazy-loads pages and headers.
'''

import cStringIO
import pycurl

import albatross
import connection

class PageLoadError(albatross.Error):
  def __init__(self, page):
    super(PageLoadError, self).__init__()
    self.page = page
  def __str__(self):
    return "\n".join([
        str(super(PageLoadError, self)),
        "URL: " + str(self.page.url),
        "needsAuth: " + str(self.page.needsAuth)
      ])

class Page(object):
  '''
  Basic page and header-loading object for albatross.
  '''
  def __init__(self, conn, url=None, needsAuth=True):
    self.connection = conn
    self.url = url
    self.needsAuth = needsAuth
    self._header = None
    self._html = None
    self._authed = None

  def checkAuthed(self, text):
    """
    Checks to ensure that the cookieString we used to make our request is still valid.
    If it's not, then there will be an error message in the HTML returned by the request.
    """
    if not text or "Sie haben das Ende des Internets erreicht." in text:
      return False
    return True

  def _getHeader(self, retries=10):
    """
    Uses cURL to read a page's headers.
    """
    for x in range(retries): # Limit the number of retries.
      header = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.NOBODY, True)
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, self.url)
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, str(self.connection.cookieString))
      pageRequest.setopt(pycurl.HEADERFUNCTION, header.write)
      try:
        pageRequest.perform()
        pageRequest.close()
        header = header.getvalue()
      except:
        continue
    return header

  def _getPage(self, retries=10):
    """
    Uses cURL to read a page.
    Retries up to retries times before returning an error.
    authed specifies whether or not we should definitely be authenticated in this request.
    """
    
    for x in range(retries): # Limit the number of retries.
      response = cStringIO.StringIO()
      header = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, self.url)
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, str(self.connection.cookieString))
      pageRequest.setopt(pycurl.WRITEFUNCTION, response.write)
      pageRequest.setopt(pycurl.HEADERFUNCTION, header.write)
      try:
        pageRequest.perform()
        requestCode = pageRequest.getinfo(pageRequest.HTTP_CODE)
        pageRequest.close()
        response = response.getvalue()
        header = header.getvalue()
      except:
        continue
      # check to see if ETI is acting up.
      if requestCode in {0:1, 404:1, 500:1, 501:1, 502:1, 503:1, 504:1}:
        raise PageLoadError(self)
      if self.needsAuth:
        if self.checkAuthed(response):
          self._authed = True
          self._html = response
          self._header = header
          return response
        else:
          if self.connection.reauthenticate():
            continue
          else:
            raise connection.UnauthorizedError(self.connection)
      else:
        return response
    raise PageLoadError(self)

  @property
  def header(self):
    if self._header is None:
      self._header = self._getHeader()
    return self._header

  @property
  def html(self):
    if self._html is None:
      self._html = self._getPage()
    return self._html

  @property
  def authed(self):
    if self._authed is None:
      # load page if not yet loaded.
      self._authed = self.checkAuthed(self.html)
    return self._authed
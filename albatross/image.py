#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Image - Image information retrieval and manipulation.
'''

import bs4
import HTMLParser
import pytz
import re
import urllib
import urlparse
import urllib2

import albatross
import connection
import page
import base
import topic

class InvalidImageError(albatross.Error):
  def __init__(self, image):
    super(InvalidImageError, self).__init__()
    self.image = image
  def __str__(self):
    return "\n".join([
        super(InvalidImageError, self).__str__(),
      "MD5: " + unicode(self.image.md5),
      "Filename: " + unicode(self.image.filename)
      ])

class Image(base.Base):
  '''
  Image-loading object for albatross.
  '''
  def __init__(self, conn, md5, filename):
    super(Image, self).__init__(conn)
    self.md5 = unicode(md5)
    self.filename = unicode(filename)
    if not isinstance(self.md5, unicode) or not isinstance(self.filename, unicode):
      raise InvalidImageError(self)
    self._related = self._relatedCount = self._topics = self._topicCount = None

  def __str__(self):
    if self._related is None:
      self.load()
    return "\n".join([
      "MD5: " + unicode(self.md5),
      "Filename: " + unicode(self.filename),
      "related: " + unicode(self.relatedCount),
      "Topics: " + unicode(self.topicCount),
      ])

  def __index__(self):
    return self.md5

  def __hash__(self):
    return self.md5

  def __eq__(self, image):
    return self.md5 == image.md5

  def set(self, attrDict):
    """
    Sets attributes of this image object with keys found in dict.
    """
    super(Image, self).set(attrDict)
    if hasattr(self, '_md5'):
      self.md5 = self._md5
      del self._md5
    if hasattr(self, '_filename'):
      self.filename = self._filename
      del self._filename
    return self

  def parse(self, html):
    """
    Given the HTML of a image page, returns a dict of attributes.
    """

    attrs = {}

    soup = bs4.BeautifulSoup(html)
    image = soup.find('img')
    if image == -1:
      # no image on this page!
      raise InvalidImageError(self)
    # fetch the attributes from the image tag.
    imageUrl = urlparse.urlparse(image.get('src'))
    pathParts = imageUrl.path.split('/')
    attrs['filename'] = pathParts[-1]
    attrs['md5'] = pathParts[-2]

    return attrs

  def load(self):
    """
    Fetches image info.
    """
    try:
      imagePage = self.connection.page('https://images.endoftheinter.net/img/' + self.md5 + '/' + self.filename)
      imagePageHtml = imagePage.html
    except page.PageLoadError as e:
      # image does not exist.
      raise InvalidImageError(self)
    if imagePage.authed:
      # hooray, start pulling info.
      self.set(self.parse(imagePageHtml))
    else:
      raise connection.UnauthorizedError(self.connection)

  def appendTopics(self, html, url, curlHandle, params):
    """
      Given the html of a topic listing of topics which contain the current image,
      append the topics on this page to the current image's topics.
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

    # parse this page and append topics to topic list.
    soup = bs4.BeautifulSoup(html)
    topicsTable = soup.find('table', {'class': 'grid'})
    if topicsTable == -1:
      # no topics in this listing.
      return
    topicRows = topicsTable.find_all('tr')[1:]
    for idx,topicRow in enumerate(topicRows):
      topicLink = topicRow.find('a')
      topicUrl = urlparse.urlparse(topicLink.get('href'))
      topicAttrs = {'title': topicLink.text, 'imagemap_order': (params['page'], idx)}
      topicAttrs['archived'] = bool(topicUrl.netloc.split('.')[0] == "archives")
      # urlparse.parse_qs doesn't work here because ???
      topicID = int(topicUrl.query.split('=')[-1])
      newTopic = self.connection.topic(topicID)
      newTopic.set(topicAttrs)
      self._topics.append(newTopic)

  def getTopics(self, maxPage=None):
    """
      Fetches all topics which contain this image.
    """
    self._topics = []
    if maxPage is None:
      # first, get the first page.
      firstPageParams = {
        'md5': self.md5,
        'page': 1
      }
      firstPageUrl = 'https://images.endoftheinter.net/imagemap.php?' + urllib.urlencode(firstPageParams)
      firstPage = self.connection.page(firstPageUrl)
      firstPageSoup = bs4.BeautifulSoup(firstPage.html)
      infobar = firstPageSoup.find('div', {'class': 'infobar'})
      if infobar == -1:
        # this image doesn't exist.
        raise InvalidImageError(self)
      numPages = int(infobar.find('span').text)
      # fetch the topics on this page.
      self.appendTopics(firstPage.html, firstPageUrl, self.connection.parallelCurl, {'page': 1})
      startPage = 2
    else:
      startPage = 1
      numPages = maxPage

    # now fetch all the pages.
    for page in range(startPage, int(numPages)+1):
      topicPageParams = urllib.urlencode({'md5': self.md5, 'page': page})
      self.connection.parallelCurl.startrequest('https://images.endoftheinter.net/imagemap.php?' + topicPageParams, self.appendTopics, {'page': page})
    self.connection.parallelCurl.finishallrequests()
    self._topics = sorted(self._topics, key=lambda x: x._imagemap_order)

  def topics(self, maxPage=None):
    """
      Returns a list of topics which contain this image.
    """
    if self._topics is None:
      self.getTopics(maxPage=maxPage)
    return self._topics

  def appendRelatedImages(self, html, url, curlHandle, params):
    """
      Given the html of a related image listing of images,
      append the images on this page to the current image's related-images.
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

    # parse this page and append images to image list.
    soup = bs4.BeautifulSoup(html)
    imageGrid = soup.find('div', {'class': 'image_grid'})
    if imageGrid == -1:
      # no images in this listing.
      return
    imageDivs = imageGrid.find_all('div', {'class': 'grid_block'})
    for idx,imageDiv in enumerate(imageDivs):
      imageLink = imageDiv.find('a')
      imageUrl = urlparse.urlparse(imageLink.get('href'))
      imageUrlParts = imageUrl.path.split('/')
      filename = imageUrlParts[-1]
      md5 = imageUrlParts[-2]
      newImage = self.connection.image(md5=md5, filename=filename)
      newImage.set({'imagemap_order': (params['page'], idx)})
      self._related.append(newImage)
    return

  def getRelatedImages(self, maxPage=None):
    """
      Fetches all images which are related to this image.
    """
    self._related = []
    if maxPage is None:
      # first, get the first page.
      firstPageParams = {
        'related': self.md5,
        'page': 1
      }
      firstPageUrl = 'https://images.endoftheinter.net/imagemap.php?' + urllib.urlencode(firstPageParams)
      firstPage = self.connection.page(firstPageUrl)
      firstPageSoup = bs4.BeautifulSoup(firstPage.html)
      infobar = firstPageSoup.find('div', {'class': 'infobar'})
      if infobar == -1:
        # this image doesn't exist.
        raise InvalidImageError(self)
      numPages = int(infobar.find('span').text)
      # fetch the images on this page.
      self.appendRelatedImages(firstPage.html, firstPageUrl, self.connection.parallelCurl, {'page': 1})
      startPage = 2
    else:
      startPage = 1
      numPages =  maxPage

    # now fetch all the pages.
    for page in range(startPage, int(numPages)+1):
      relatedPageParams = urllib.urlencode({'related': self.md5, 'page': page})
      self.connection.parallelCurl.startrequest('https://images.endoftheinter.net/imagemap.php?' + relatedPageParams, self.appendRelatedImages, {'page': page})
    self.connection.parallelCurl.finishallrequests()
    self._related = sorted(self._related, key=lambda x: x._imagemap_order)

  def related(self, maxPage=None):
    """
      Returns a list of images that are related to this image.
    """
    if self._related is None:
      self.getRelatedImages(maxPage=maxPage)
    return self._related

  @property
  def relatedCount(self):
    """
      Returns a count of images that are related to this image.
    """
    if self._relatedCount is None:
      self._relatedCount = len(self.related())
    return self._relatedCount

  @property
  def topicCount(self):
    """
      Returns a count of topics containing this image.
    """
    if self._topicCount is None:
      self._topicCount = len(self.topics())
    return self._relatedCount
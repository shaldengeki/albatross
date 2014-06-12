#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    post_nodes - classes for different types of content in a post, i.e. text, links, spoilers, quotes, images
'''

import re
import bs4

import albatross
import base
import image

class InvalidNodeError(albatross.Error):
  def __init__(self, html, message=None):
    super(InvalidNodeError, self).__init__(message=message)
    self.html = html
  def __str__(self):
    return "\n".join([
      super(InvalidNodeError, self).__str__(),
      "HTML: " + unicode(self.html)
    ])

def get_child_nodes(conn, node):
  """
    Returns a list of child nodes within the current node.
  """
  dom = bs4.BeautifulSoup(node)
  first_node = dom.children.next()
  child_nodes = []
  for dom_node in first_node.children:
    if is_link_node(dom_node):
      child_nodes.append(LinkNode(conn, dom_node))
    elif is_spoiler_node(dom_node):
      child_nodes.append(SpoilerNode(conn, dom_node))
    elif is_quote_node(dom_node):
      child_nodes.append(QuoteNode(conn, dom_node))
    elif is_image_container_node(dom_node):
      child_nodes.append(ImageContainerNode(conn, dom_node))
    else:
      child_nodes.append(TextNode(conn, dom_node))
  return child_nodes


class BaseNode(base.Base):
  """
  Base class for different types of content in a post, i.e. text, links, spoilers, quotes, images
  """
  def __init__(self, conn, html):
    super(BaseNode, self).__init__(conn)
    self.html = unicode(html)

  def load(self):
    """
      Called upon first access to any @loadable property.
      Should set node type-specific values, i.e. for an image the md5 hash and filename.
    """
    raise NotImplementedError

  def get_child_nodes(self):
    return get_child_nodes(self.connection, self.html)

  def render(self):
    """
      Returns a string representation of the current post node and all its children.
    """
    return self.html

  @property
  @base.loadable
  def nodes(self):
    return self._nodes


# Text node stuff.

class TextNode(BaseNode):
  def __init__(self, conn, html):
    super(TextNode, self).__init__(conn, html)

  def __repr__(self):
    return '<TextNode ' + unicode(self.html).encode('utf-8') + '>'

  def __str__(self):
    return unicode(self.html).encode('utf-8')

  def __eq__(self, text):
    return self.html == unicode(text)

  def __contains__(self, text):
    return text in self.html

  def load(self):
    pass

  def get_child_nodes(self):
    return []

# Link node stuff.

class InvalidLinkNodeError(InvalidNodeError):
  pass

def is_link_node(node):
  return node.name == u'a' and u'l' in node.get('class')

class LinkNode(BaseNode):
  def __init__(self, conn, html):
    super(LinkNode, self).__init__(conn, html)
    self._href = None

  def __repr__(self):
    return '<LinkNode ' + unicode(self.href).encode('utf-8') + '>'

  def __str__(self):
    return unicode(self.href).encode('utf-8')

  def load(self):
    dom = bs4.BeautifulSoup(self.html)
    link_elt = dom.find('a')
    if not link_elt:
      raise InvalidLinkNodeError(self.html, message="No link element found")
    self._href = link_elt.get('href')

  def get_child_nodes(self):
    return []

  @property
  @base.loadable
  def href(self):
    return self._href

# Quote node stuff.

class InvalidQuoteNodeError(InvalidNodeError):
  pass

def is_quote_node(node):
  return node.name == u'div' and u'quoted-message' in node.get('class')

class QuoteNode(BaseNode):
  def __init__(self, conn, html):
    super(QuoteNode, self).__init__(conn, html)
    self._quoted = None

  def __repr__(self):
    return '<QuoteNode Post#' + unicode(self.quoted.id) + ' Topic#' + unicode(self.quoted.topic.id) + '>'

  def __eq__(self, post):
    return self.quoted.id == post.id

  def load(self):
    dom = bs4.BeautifulSoup(self.html)
    quote_elt = dom.find('div', {'class': 'quoted-message'})
    if not quote_elt:
      raise InvalidQuoteNodeError(self.html, message="No quote element found")

    # get post, user info from this quote.
    msgid = quote_elt.get('msgid').split(',')
    topic_id = int(msgid[1])
    post_id = int(msgid[2][:-2])
    user_link = quote_elt.find('a')
    user_id = int(re.search('user=(?P<id>[0-9]+)', user_link.get('href')).group('id'))
    user_name = user_link.text

    self._quoted = self.connection.post(post_id, topic=self.connection.topic(topic_id))
    self._quoted.set({
      'user': self.connection.user(user_id).set({'name': user_name})
    })

  @property
  @base.loadable
  def quoted(self):
    return self._quoted

# Image node stuff.
# Images are contained within a container div, classed 'imgs'

class InvalidImageContainerNodeError(InvalidNodeError):
  pass

def is_image_container_node(node):
  return node.name == u'div' and u'imgs' in node.get('class')

class InvalidImageNodeError(InvalidNodeError):
  pass

def is_image_node(node):
  return node.name == u'a' and node.get('imgsrc')

class ImageContainerNode(BaseNode):
  def __init__(self, conn, html):
    super(ImageContainerNode, self).__init__(conn, html)
    self._images = None

  def __repr__(self):
    return '<ImageContainerNode: ' + ', '.join(map(lambda x: x.md5, self.images))  + '>'

  def __contains__(self, image):
    return image in self.images

  def load(self):
    dom = bs4.BeautifulSoup(self.html)
    container_elt = dom.find('div', {'class': 'imgs'})
    if not container_elt:
      raise InvalidImageContainerNodeError(self.html, message="No image container found")

    contained_images = container_elt.find_all('a', imgsrc=True)
    images = []
    for image_node in contained_images:
      image_info = '/imap'.join(image_node.get('href').split('/imap/')[1:]).split('/')
      md5 = image_info[0]
      filename = '/'.join(image_info[1:])
      placeholder = image_node.find('span', {'class': 'img-placeholder'})
      dimensions = placeholder.get('style').split(';')
      for dimension in dimensions:
        if dimension.startswith('width'):
          width = dimension.split(':')[1]
        elif dimension.startswith('height'):
          height = dimension.split(':')[1]
      images.append(image.Image(self.connection, md5=md5, filename=filename, width=width, height=height))
    self._images = images

  @property
  @base.loadable
  def images(self):
    return self._images

# Spoiler node stuff.
# TODO

def is_spoiler_node(node):
  return False

class SpoilerNode(BaseNode):
  pass
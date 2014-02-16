#!/usr/bin/env python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl

    Base - Provides base object for other Albatross objects.
'''

import albatross
import connection

def loadable(func):
  cached_name = '_' + func.__name__
  def _decorator(self, *args, **kwargs):
    if getattr(self, cached_name) is None:
      self.load()
    return func(self, *args, **kwargs)
  return _decorator

class Base(object):
  '''
    Provides autoloading, auto-setting functionality for other Albatross objects.
  '''
  def __init__(self, conn):
    self.connection = conn

  def load(self):
    pass

  def set(self, attr_dict):
    """
    Sets attributes of this user object with keys found in dict.
    """
    for key in attr_dict:
      if key == 'id':
        self.id = attr_dict[key]
      else:
        setattr(self, "_" + key, attr_dict[key])
    return self
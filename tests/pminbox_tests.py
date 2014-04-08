from nose.tools import *
import albatross
import datetime
import pytz

class testPMInboxClass(object):
  @classmethod
  def setUpClass(self):
    # reads ETI login credentials from credentials.txt and cookieString.txt in the current directory.
    credentials = open('credentials.txt', 'r').readlines()[0].strip().split(',')
    
    self.username = credentials[0]
    self.password = credentials[1].rstrip()
    self.etiConn = albatross.Connection(username=self.username, password=self.password, loginSite=albatross.SITE_MOBILE)

    self.inbox = self.etiConn.inbox()

  def testThreads(self):
    assert isinstance(self.inbox, albatross.PMInbox)

  def testThreadCount(self):
    assert len(self.inbox) > 0
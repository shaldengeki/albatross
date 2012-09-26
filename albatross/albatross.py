#!/usr/bin/python
'''
    albatross - Provides link- and board-scraping functions for ETI.
    License - WTF Public License, Version 2.0 <http://sam.zoy.org/wtfpl/COPYING>
    Author - Shal Dengeki <shaldengeki@gmail.com>
    REQUIRES - pytz, pycurl, pyparallelcurl
'''

import calendar
import cStringIO
import datetime
import json
import os
import re
import sys
import time
import urllib
import urllib2

import pytz
import pycurl
import pyparallelcurl

SITE_MAIN = {"url":"https://endoftheinter.net/","fields":{"username":"b","password":"p"}}
SITE_MOBILE = {"url":"https://iphone.endoftheinter.net/","fields":{"username":"username","password":"password"}}

def printUsageAndQuit():
  """
  Prints usage information and exits.
  """
  print "usage: [--report-links] [--num-requests n] username password startID endID"
  sys.exit(1)

class Albatross(object):
  '''
  Provides programmatic access to link and board information.
  '''
  def __init__(self, username="", password="", cookieString="", cookieFile="", reauth=None, loginSite=SITE_MAIN, num_requests=20):
    """
    Albatross constructor.
    Expects either a username + password pair, or a cookie string and possibly a cookie file to read updated cookie strings from.
    If a username + password or cookie string + file pair is provided, then will attempt to reauthenticate if a logout is detected.
    To prevent this behavior, call the constructor with the reauth argument set to False.
    """
    self.username = username
    self.password = password
    self.loginSite = loginSite
    self.cookieFile = cookieFile
    self.num_requests = num_requests
    if username and password:
      self.cookieString = self.login(self.username, self.password)
      self.reauth = True
    elif cookieString:
      self.cookieString = cookieString
      if os.path.exists(self.cookieFile):
        self.reauth = True
      else:
        self.reauth = False
    if reauth is not None:
      self.reauth = bool(reauth)
    if not self.cookieString or not self.checkLoggedIn():
      print "Warning: invalid credentials provided."
    self.setParallelCurlObject()
    
  def parseCookieHeader(self, string):
    """
    Given a cookie response header returned by pyCurl, return an array of cookie key/values.
    """
    
    string_array = str(string).split("\r\n")
    cookieList = []
    for line in string_array:
      if line.startswith("Set-Cookie:"):
        cookieList.append('='.join(line[11:-1].strip().split(";")[0].split("=")))
        
    cookieString = '; '.join(cookieList)
    return cookieString
  
  def login(self, username, password):
    """
    Logs into LL using the provided username and password, returning the resultant cookie string.
    """
    response = cStringIO.StringIO()
    loginHeaders = pycurl.Curl()
    
    loginHeaders.setopt(pycurl.SSL_VERIFYPEER, False)
    loginHeaders.setopt(pycurl.SSL_VERIFYHOST, False)
    loginHeaders.setopt(pycurl.POST, 1)
    loginHeaders.setopt(pycurl.HEADER, True)
    loginHeaders.setopt(pycurl.URL, self.loginSite["url"]+'index.php')
    loginHeaders.setopt(pycurl.POSTFIELDS, urllib.urlencode(dict([(self.loginSite["fields"]["username"], str(username)), (self.loginSite["fields"]["password"], str(password)), ('r', '')])))
    loginHeaders.setopt(pycurl.USERAGENT, 'Albatross')
    loginHeaders.setopt(pycurl.WRITEFUNCTION, response.write)
    
    try:
      loginHeaders.perform()
      loginHeaders.close()
    except:
      return False
    
    cookieHeader = response.getvalue()
    if re.search(r'Sie bitte 15 Minuten', cookieHeader) or not re.search(r'session=', cookieHeader):
      return False

    cookieString = self.parseCookieHeader(cookieHeader)
    self.cookieString = cookieString
    self.setParallelCurlObject()
    return cookieString
  
  def setParallelCurlObject(self):
    """
    (Re)sets the parallelCurl object to use the current cookieString.
    """
    self.parallelCurlOptions = {
      pycurl.SSL_VERIFYPEER: False,
      pycurl.SSL_VERIFYHOST: False,
      pycurl.FOLLOWLOCATION: True, 
      pycurl.COOKIE: self.cookieString
    }
    try:
      self.parallelCurl.setoptions(self.parallelCurlOptions)
    except AttributeError:
      self.parallelCurl = pyparallelcurl.ParallelCurl(self.num_requests, self.parallelCurlOptions)
    
  def reauthenticate(self):
    """
    Reauthenticates and resets authentication attributes if need be and reauth attribute is True.
    """
    if self.reauth:
      if self.checkLoggedIn():
        return True
      if self.username and self.password:
        cookieString = self.login(self.username, self.password)
      elif os.path.exists(self.cookieFile):
        cookieString = open(self.cookieFile, 'r').readline().strip('\n')
      if cookieString and cookieString != self.cookieString:
        self.cookieString = cookieString
        self.setParallelCurlObject()
        return True
    return False
  
  def getEnclosedString(self, text, startString='', endString='', multiLine=False, greedy=False):
    """
    Given some text and two strings, return the string that is encapsulated by the first sequence of these two strings in order.
    If either string is not found or text is empty, return false.
    Multiline option makes the return possibly multi-line.
    """
    if not text or not len(text):
      return False
    flags = False
    if multiLine:
      flags = re.DOTALL
    greedyPart = "?"
    if greedy:
      greedyPart = ""    
    stringMatch = re.search(str(startString) + r'(?P<return>.+' + greedyPart + r')' + str(endString), text, flags=flags)
    if not stringMatch:
      return False
    if isinstance(stringMatch.group('return'), unicode):
      return stringMatch.group('return')
    else:
      return unicode(stringMatch.group('return'), encoding='latin-1').encode('utf-8')
    
  def getPageHeader(self, url, retries=10):
    """
    Uses cURL to read a page's headers.
    """
    for x in range(retries): # Limit the number of retries.
      response = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.NOBODY, True)
      pageRequest.setopt(pycurl.HEADER, True)
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, url)
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, str(self.cookieString))
      pageRequest.setopt(pycurl.WRITEFUNCTION, response.write)
      try:
        pageRequest.perform()
        pageRequest.close()
        response = response.getvalue()
      except:
        continue
      if self.checkPageAuthed(response):
        return response
      else:
        if self.reauthenticate():
          return self.getPageHeader(url, retries=retries-x-1)
        else:
          return False
    return False  

  def getPage(self, url, retries=10, authed=True):
    """
    Uses cURL to read a page.
    Retries up to retries times before returning an error.
    authed specifies whether or not we should definitely be authenticated in this request.
    """
    
    for x in range(retries): # Limit the number of retries.
      response = cStringIO.StringIO()
      pageRequest = pycurl.Curl()
      
      pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
      pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
      pageRequest.setopt(pycurl.URL, url)
      pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
      pageRequest.setopt(pycurl.COOKIE, str(self.cookieString))
      pageRequest.setopt(pycurl.WRITEFUNCTION, response.write)
      try:
        pageRequest.perform()
        pageRequest.close()
        response = response.getvalue()
      except:
        continue
      if authed:
        if self.checkPageAuthed(response):
          return response
        else:
          if self.reauthenticate():
            continue
          else:
            return False
      else:
        return response
    return False
    
  def checkLoggedIn(self):
    """
    Checks if the current cookie string is still valid.
    Returns boolean value reflecting this.
    """
    
    mainPageHTML = self.getPage('http://endoftheinter.net/main.php', authed=False)
    if not mainPageHTML or 'stats.php">Stats</a>' not in mainPageHTML:
      return False
    else:
      return True
    
  def checkPageAuthed(self, text):
    """
    Checks to ensure that the cookieString we used to make our request is still valid.
    If it's not, then there will be an error message in the HTML returned by the request.
    """
    if text is '' or "Sie haben das Ende des Internets erreicht." in text:
      return False
    return True
    
  def getLinkPage(self, linkID, pageNum=1, retries=10):
    """
    Grabs a link's page, given its linkID, and returns the HTML.
    Upon failure returns False.
    """
    for x in range(retries):
      linkPage = pycurl.Curl()
      response = cStringIO.StringIO()
      linkPage.setopt(pycurl.COOKIE, str(self.cookieString))
      linkPage.setopt(pycurl.URL, 'https://links.endoftheinter.net/linkme.php?l=' + str(linkID) + '&page=' + str(pageNum))
      linkPage.setopt(pycurl.USERAGENT, 'Albatross')
      linkPage.setopt(pycurl.SSL_VERIFYPEER, False)
      linkPage.setopt(pycurl.SSL_VERIFYHOST, False)
      linkPage.setopt(pycurl.WRITEFUNCTION, response.write)
      try:
        linkPage.perform()
        linkPage.close()
      except:
        continue
      linkPageHTML = response.getvalue()
      if self.checkPageAuthed(linkPageHTML):
        return linkPageHTML
      else:
        if self.reauthenticate():
          return self.getLinkPage(linkID, pageNum, retries=retries-x-1)
        else:
          return False
    return False
    
  def getLinkTitle(self, text):
    """
    Given HTML of a link page, return link title or False if title not found.
    """
    return self.getEnclosedString(text, '<h1>', '</h1>')

  def getLinkLink(self, text):
    """
    Given HTML of a link page, return link field of link.
    """
    return self.getEnclosedString(text, ' target="_blank">', '</a>')
    
  def getLinkCreator(self, text):
    """
    Given HTML of a link page, returns a dict with userid and username of user who created this link.
    """
    creatorText = self.getEnclosedString(text, r'\<b\>Added by\:\<\/b\> \<a href\=\"profile\.php\?user\=', r'\<\/a\>\<br \/\>')
    if not creatorText:
      return False
    else:
      creatorList = creatorText.split('">')
      return dict([('userid', creatorList[0]), ('username', creatorList[1])])

  def getLinkDate(self, text):
    """
    Given HTML of a link page, returns the date it was added.
    """
    return self.getEnclosedString(text, '<b>Date:</b> ', '<br />')
    
  def getLinkDateUnix(self, text):
    """
    Given HTML of a link page, return the UNIX timestamp it was added.
    """
    if self.getLinkDate(text):
      try:
        return True and int(calendar.timegm(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getLinkDate(text), "%m/%d/%Y %I:%M:%S %p")).utctimetuple())) or False
        #return True and int(time.mktime(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getLinkDate(text), "%m/%d/%Y %I:%M:%S %p")).astimezone(pytz.timezone(time.tzname[0])).timetuple())) or False
      except ValueError:
        return False
    else:
      return False

  def getLinkCode(self, text):
    """
    Given HTML of a link page, returns the link code.
    """
    return self.getEnclosedString(text, r'\<b\>Code:\<\/b\> \<a href\=\"linkme\.php\?l\=\d+\"\>', r'</a><br />')

  def getLinkHits(self, text):
    """
    Given HTML of a link page, returns the number of hits on this link.
    """
    hitText = self.getEnclosedString(text, '<b>Hits:</b> ', r'<br />')
    return True and int(hitText) or False

  def getLinkRating(self, text):
    """
    Given HTML of a link page, returns the rating of this link.
    """
    ratingText = self.getEnclosedString(text, '<b>Rating:</b> ', r'/10')
    return True and float(ratingText) or False

  def getLinkVotes(self, text):
    """
    Given HTML of a link page, returns the number of votes on this link.
    """
    votesText = self.getEnclosedString(text, r'\/10 \(based on ', r' votes\)\<br \/\>')
    return True and int(votesText) or False

  def getLinkRank(self, text):
    """
    Given HTML of a link page, returns this link's rank.
    """
    rankText = self.getEnclosedString(text, r'<b>Rank:</b> ', r'<br/>')
    return True and int(rankText) or False

  def getLinkCategories(self, text):
    """
    Given HTML of a link page, returns list of link categories.
    """
    categoryText = self.getEnclosedString(text, '<b>Categories:</b> ', '<br />')
    if not categoryText:
      return False
    else:
      return categoryText.split(', ')

  def getLinkDescription(self, text):
    """
    Given HTML of a link page, returns the link description.
    """
    return self.getEnclosedString(text, '<b>Description:</b>\s+', '  <br /><br />', multiLine=True)
    
  def getLinkCommentID(self, text):
    """
    Given HTML of a link comment, returns the comment ID.
    """
    return int(self.getEnclosedString(text, '<a href="/message\.php\?id\=', '\&amp\;topic'))

  def getMaxLinkID(self):
    """
    Returns the int value of the maximum link ID on ETI.
    """
    return int(self.getEnclosedString(self.getPage('https://links.endoftheinter.net/links.php?mode=new'), r'\<td\>\<a href\=\"linkme\.php\?l\=', r'\"\>'))
    
  def appendLinkPageComments(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a link comment listing as fed in by pyparallelcurl and appends the comments contained within to the list of comments in paramArray.
    """
    linkID = paramArray[0]
    comments = paramArray[1]
    
    if not text:
      return False
    elif not self.checkPageAuthed(text):
      if self.reauthenticate():
        self.parallelCurl.startrequest(url, self.appendLinkPageComments, paramArray)
    else:
      # parse this page and append comments to comment list.
      thisPageComments = self.getPagePosts(text)[:-1]
      for comment in thisPageComments:
        comments.append(dict([("linkID",int(linkID)), ("commentID", self.getLinkCommentID(comment)), ("username",self.getPostUsername(comment)), ("userID",self.getPostUserID(comment)), ("date",self.getPostDateUnix(comment)), ("sig", self.getPostSig(comment)), ("text",self.getPostText(comment))]))

  def getLinkComments(self, linkID, linkNumPages=False):
    """
    Given a linkID, return a list of comment dicts in this topic.
    Performs operation in parallel.
    """
    comments = []
    if not linkNumPages:
      # get the first page of this link to obtain a range of pages.
      firstPageHTML = self.getLinkPage(linkID=linkID, pageNum=1)
      if not firstPageHTML:
        return False
      linkNumPages = self.getTopicNumPages(firstPageHTML)
      # parse this page and initialize comment list to the first page of comments.
      firstPageComments = self.getPagePosts(firstPageHTML)[:-1]
      for comment in firstPageComments:
        comments.append(dict([("linkID",int(linkID)), ("commentID", self.getLinkCommentID(comment)), ("username",self.getPostUsername(comment)), ("userID",self.getPostUserID(comment)), ("date",self.getPostDateUnix(comment)), ("sig", self.getPostSig(comment)), ("text",self.getPostText(comment))]))
      startPageNum = 2
    else:
      startPageNum = 1
    # now loop over all the other pages (if there are any)
    for pageNum in range(startPageNum, int(linkNumPages)+1):
      self.parallelCurl.startrequest('https://links.endoftheinter.net/linkme.php?l=' + str(linkID) + '&page=' + str(pageNum), self.appendLinkPageComments, [linkID, comments])
    self.parallelCurl.finishallrequests()

    # finally, return the post list.
    return sorted(comments, key=lambda comment: comment['commentID'])

  def getLinkDict(self, linkID):
    """
    Takes a requested linkID and returns a dict containing the link's information.
    """
    linkPageHTML = self.getLinkPage(linkID)
    if not linkPageHTML:
      return False
    linkNumPages = self.getTopicNumPages(linkPageHTML)
    return {"linkid":int(linkID), "title":str(self.getLinkTitle(linkPageHTML)), "link":str(self.getLinkLink(linkPageHTML)), "creator":self.getLinkCreator(linkPageHTML), "date":int(self.getLinkDateUnix(linkPageHTML)), "code":str(self.getLinkCode(linkPageHTML)), "hits":int(self.getLinkHits(linkPageHTML)), "rating":float(self.getLinkRating(linkPageHTML)), "votes":int(self.getLinkVotes(linkPageHTML)), "rank":int(self.getLinkRank(linkPageHTML)), "categories":self.getLinkCategories(linkPageHTML), "description":str(self.getLinkDescription(linkPageHTML)), "comments":self.getLinkComments(linkID=linkID,linkNumPages=linkNumPages)}
    
  def getLinkListingDicts(self, text):
    """
    Given the HTML of a link listing page, returns a list of dicts with all the available information for each of the links listed.
    """
    newLinksHTML = text.split('<tr class="r')[1:]
    linkListingDicts = []
    for linkRow in newLinksHTML:
      singleLinkRows = linkRow.split('<td>')[1:]
      linkID = int(self.getEnclosedString(singleLinkRows[0], '\<a\ href\=\"linkme\.php\?l\=', '\"\>'))
      linkTitle = self.getEnclosedString(singleLinkRows[0], '\<a\ href\=\"linkme\.php\?l\=' + str(linkID) + '\"\>', '\<\/a\>\<\/td\>')
      # linkDate = int(time.mktime(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getEnclosedString(singleLinkRows[1], '', '\<\/td\>'), "%m/%d/%Y %H:%M")).astimezone(pytz.timezone(time.tzname[0])).timetuple()))
      linkDate = int(calendar.timegm(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getEnclosedString(singleLinkRows[1], '', '\<\/td\>'), "%m/%d/%Y %H:%M")).utctimetuple()))
      linkUserID = int(self.getEnclosedString(singleLinkRows[2], '\<a\ href\=\"profile\.php\?user\=', '\"\>'))
      linkUsername = self.getEnclosedString(singleLinkRows[2], '\<a\ href\=\"profile\.php\?user\=' + str(linkUserID) + '\"\>', '\<\/a\>\<\/td\>')
      linkVoteNum = int(self.getEnclosedString(singleLinkRows[3], '\(based\ on\ ', '\ votes\)\<\/td\>'))
      linkRating = float(self.getEnclosedString(singleLinkRows[3], '', '\/10'))
      linkRank = int(self.getEnclosedString(singleLinkRows[4], '', '\<\/td\>'))
      linkListingDicts.append(dict([('linkID', linkID), ('title', linkTitle), ('creator', dict([('userid', linkUserID), ('username', linkUsername)])), ('date', linkDate), ('rating', linkRating), ('votes', linkVoteNum), ('rank', linkRank)]))
    return linkListingDicts
    
  def reportLink(self, linkID, reason, comments):
    """
    Reports linkID for specified reason and appends comments.
    """
    #  if not cookieString or not int(linkID) or not int(reason) or not len(comments):
    #    return False
    #  params = urllib.urlencode(dict([('r', int(reason)), ('c', comments)]))
    #  report_link = opener.open('https://links.endoftheinter.net/linkreport.php?l='+str(int(linkID)), params)
    #  data = report_link.read()
    #  report_link.close()
    # LL doesn't provide any feedback upon reporting a link so we have to assume that all went well.
    return True
    
  def checkLinkDeleted(self, text):
    """
    Returns True if link has been deleted; False if it hasn't.
    """
    deletedMatch = re.search(r'\<em\>This link has been deleted, and is no longer available\<\/em\>', text)
    return bool(deletedMatch)
    
  def checkLinkExists(self, text):
    """
    Checks if the selected link is not deleted and is a valid link (i.e. not out-of-bounds).
    Returns True or False to reflect if link exists.
    """
    invalid_match = re.search(r'\<em\>Invalid link\!\<\/em\>', text)
    return (not invalid_match and not self.checkLinkDeleted(text))
    
  def checkLinkNeedsReporting(self, text, url, curlHandle, paramArray):
    """
    Checks to see if a link needs to be reported.
    Checks several things:
    1.  If there are [TAGS] in the title, checks to ensure categories are properly set for those tags.
    2.  If there are links to sites specified by site_dict within the link description or actual link, 
        checks those to see if they're down and if this link is tagged with the 'Uploads' category.
    Returns False if all the checks pass (or the link is deleted), a list of reasons if not.
    """
    linkID = paramArray[0]
    startID = paramArray[1]
    endID = paramArray[2]
    tag_dict = paramArray[3]
    site_dict = paramArray[4]
    
    if not self.checkPageAuthed(text):
      if self.reauthenticate():
        self.parallelCurl.startrequest(url, self.checkLinkNeedsReporting, paramArray)
        return

    if not self.checkLinkExists(text):
      return False

    if self.checkLinkDeleted(text):
      return False
    
    reasonList = []
    
    # check to make sure that any [TAGS] in the title are properly-reflected in the categories.
    title = self.getLinkTitle(text)
    title_tags = re.findall(r'\[\S+?\]', title)
    categories = self.getLinkCategories(text)
    for tag in title_tags:
      if tag.upper() in tag_dict:
        for required_tag in tag_dict[tag.upper()]:
          if categories and required_tag not in categories:
            reasonList.append((3, 'Needs category: ' + required_tag))
    
    # check link's link and description to see if there are links to popular upload sites.
    link = self.getLinkLink(text)
    if link:
      link_match = re.search(r'(\w+\.com)', link)
      if link_match and link_match.groups()[0] in site_dict:
        if 'Uploads' not in categories:
          reasonList.append((3, 'Needs category: Uploads'))
        base_url = link_match.groups()[0]
        link_external_site = urllib2.urlopen(link)
        site_text = link_external_site.read()
        link_external_site.close()
        if site_dict[base_url] in site_text:
          reasonList.append((2, 'Dead link.'))
    else:
      link = ''
    # if there are upload links in the link or description and this link isn't tagged as upload, flag this link to be reported.
    description = self.getLinkDescription(text)
    if description:
      allText_matches = re.findall(r'(\w+\.com)', str(link) + str(description))
      if allText_matches:
        for base_url in allText_matches:
          if base_url in site_dict and 'Uploads' not in categories:
            reasonList.append((3, 'Needs category: Uploads'))

    if reasonList:
      reportComment = ""
      for reasonTuple in reasonList:
        if not reportComment:
          reportComment = reasonTuple[1]
        else:
          reportComment = reportComment + "\r\n" + reasonTuple[1]
        lastReason = reasonTuple[0]
      if int(linkID) and int(lastReason) and len(reportComment):
        self.parallelCurl.startrequest('https://links.endoftheinter.net/linkreport.php?l='+str(int(linkID)), self.reportLink, [], post_fields = urllib.urlencode(dict([('r', int(lastReason)), ('c', reportComment)])))
        print "Reported linkID " + str(linkID) + " (type " + str(lastReason) + "): " + ", ".join(reportComment.split("\r\n"))
    # waiting sucks.
    if linkID % 100 == 0:
      print "Progress: " + str(round(100*(linkID - startID)/(endID - startID), 2)) + "% (" + str(linkID) + "/" + str(endID) + ")"

  def appendLinkPageListingDicts(self, text, url, curlHandle, paramArray):
    links = paramArray[0]
    
    if not self.checkPageAuthed(text):
      if self.reauthenticate():
        self.parallelCurl.startrequest(url, self.appendLinkPageListingDicts, paramArray)
        return
    
    for linkDict in self.getLinkListingDicts(text):
      links.append(linkDict)
      
  def getNewLinks(self, recurse=True):
    """
    Returns a list of dicts for the newest links on links.php?mode=new.
    """
    newLinksPage = self.getPage('http://links.endoftheinter.net/links.php?mode=new')
    if not newLinksPage:
      return False
    links = self.getLinkListingDicts(newLinksPage)
    if recurse:
      linkNumPages = self.getTopicNumPages(newLinksPage)
      for pageNum in range(2, int(linkNumPages)+1):
        self.parallelCurl.startrequest('http://links.endoftheinter.net/links.php?mode=new&page=' + str(pageNum), self.appendLinkPageListingDicts, [links])
      self.parallelCurl.finishallrequests()
    return links
    
  def reportLinks(self, startID, endID):
    """
    Iterates through provided range of linkIDs, reporting those which are mis-categorized or simply down.
    """
    
    # dict of tuples - first item is a title [TAG], second item is a list of categories 
    # that should be included for all links containing the title [TAG].
    
    tag_dict = dict([
                    ('[ANIME]', ['Anime', 'Videos']), 
                    ('[EBOOK]', ['Books']), 
                    ('[MAGAZINE]', ['Books']), 
                    ('[TEXTBOOK]', ['Books', 'Educational']), 
                    ('[DREAMCAST]', ['Console Games']), 
                    ('[GCN]', ['Console Games']), 
                    ('[N64]', ['Console Games']), 
                    ('[PS1]', ['Console Games']), 
                    ('[PS2]', ['Console Games']), 
                    ('[PS3]', ['Console Games']), 
                    ('[PSX]', ['Console Games']), 
                    ('[WII]', ['Console Games']), 
                    ('[XBOX360]', ['Console Games']), 
                    ('[NDS]', ['Portable Games']), 
                    ('[PSP]', ['Portable Games']), 
                    ('[PORN]', ['Porn', 'Videos']), 
                    ('[GAY PORN]', ['Gay Porn', 'Videos']), 
                    ('[HENTAI]', ['Hentai']), 
                    ('[MOVIE]', ['Movies']), 
                    ('[MUSIC]', ['Music']), 
                    ('[NEWS]', ['News Article', 'Text']), 
                    ('[TV]', ['TV Shows', 'Videos'])
                    ])

    # dict of upload sites used, with string returned if link is down.
    site_dict = dict([('megaupload.com', 'Unfortunately, the link you have clicked is not available.'), 
                      ('mediafire.com', 'Invalid or Deleted File.')])
    
    # now loop over all the links in this range, reporting those which have issues.
    for linkID in range(startID, endID):
      self.parallelCurl.startrequest('https://links.endoftheinter.net/linkme.php?l='+str(linkID), self.checkLinkNeedsReporting, [linkID, startID, endID, tag_dict, site_dict])

    self.parallelCurl.finishallrequests()

  def getTopicPage(self, topicID, pageNum=1, archived=False, userID="", retries=10):
    """
    Grabs a topic's message listing, given its topicID (and optional boardID, userID, archived, and page number parameters), and returns the HTML.
    Upon failure returns False.
    """
    if archived:
      subdomain="archives"
    else:
      subdomain="boards"
    for x in range(retries):
      topicPage = pycurl.Curl()
      response = cStringIO.StringIO()
      topicPage.setopt(pycurl.COOKIE, str(self.cookieString))  
      topicPage.setopt(pycurl.USERAGENT, 'Albatross')
      topicPage.setopt(pycurl.URL, 'http://' + subdomain + '.endoftheinter.net/showmessages.php?topic=' + str(topicID) + '&u=' + str(userID) + '&page=' + str(pageNum))
      topicPage.setopt(pycurl.SSL_VERIFYPEER, False)
      topicPage.setopt(pycurl.SSL_VERIFYHOST, False)
      topicPage.setopt(pycurl.WRITEFUNCTION, response.write)
      try:
        topicPage.perform()
        topicPage.close()
      except:
        continue
      topicPageHTML = response.getvalue()
      if self.checkPageAuthed(topicPageHTML):
        return topicPageHTML
      else:
        if self.reauthenticate():
          return self.getTopicPage(topicID, pageNum=pageNum, archived=archived, userID=userID, retries=retries-x-1)
        else:
          return False
    return False
    
  def appendTopicPagePosts(self, text, url, curlHandle, paramArray):
    """
    Takes the HTML of a topic message listing as fed in by pyparallelcurl and appends the posts contained within to the list of posts in paramArray.
    """
    topicID = paramArray[0]
    posts = paramArray[1]
    
    if not text:
      return False
    
    if not self.checkPageAuthed(text):
      if self.reauthenticate():
        self.parallelCurl.startrequest(url, self.appendTopicPagePosts, paramArray)
        return
      
    # parse this page and append posts to post list.
    thisPagePosts = self.getPagePosts(text)
    for post in thisPagePosts:
      posts.append(dict([("postID",self.getPostID(post)), ("topicID",int(topicID)), ("username",self.getPostUsername(post)), ("userID",self.getPostUserID(post)), ("date",self.getPostDateUnix(post)), ("sig", self.getPostSig(post)), ("text",self.getPostText(post))]))

  def getTopicPosts(self, topicID, archived=False, topicNumPages=False, startPageNum=1, userID=""):
    """
    Given a topicID and boardID (and whether or not it's in the archives), return a list of post dicts in this topic.
    Performs operation in parallel.
    """
    if archived:
      topicSubdomain = "archives"
    else:
      topicSubdomain = "boards"
    
    posts = []
    if not topicNumPages:
      # get the first page of this topic to obtain a range of pages.
      firstPageHTML = self.getTopicPage(topicID=topicID, pageNum=startPageNum, archived=archived, userID=userID)
      topicNumPages = self.getTopicNumPages(firstPageHTML)
      if not firstPageHTML or not topicNumPages:
        return False
      # parse this page and initialize post list to the first page of posts.
      firstPagePosts = self.getPagePosts(firstPageHTML)
      for post in firstPagePosts:
        posts.append(dict([("postID",self.getPostID(post)), ("topicID",int(topicID)), ("username",self.getPostUsername(post)), ("userID",self.getPostUserID(post)), ("date",self.getPostDateUnix(post)), ("sig", self.getPostSig(post)), ("text",self.getPostText(post))]))
      startPageNum += 1
    # now loop over all the other pages (if there are any)
    for pageNum in range(startPageNum, int(topicNumPages)+1):
      topicPageParams = urllib.urlencode([('topic', str(topicID)), ('u', str(userID)), ('page', str(pageNum))])
      self.parallelCurl.startrequest('https://' + topicSubdomain + '.endoftheinter.net/showmessages.php?' + topicPageParams, self.appendTopicPagePosts, [topicID, posts])
    self.parallelCurl.finishallrequests()

    # finally, return the post list.
    return sorted(posts, key=lambda post: post['postID'])
    
  def getTopicDateUnix(self, text):
    """
    Given a string representation of a topic's date, returns the unix timestamp of said topic date.
    """
    try:
      #return True and int(time.mktime(pytz.timezone("US/Central").localize(datetime.datetime.strptime(text, "%m/%d/%Y %H:%M")).astimezone(pytz.timezone(time.tzname[0])).timetuple())) or False
      return True and int(calendar.timegm(pytz.timezone("US/Central").localize(datetime.datetime.strptime(text, "%m/%d/%Y %H:%M")).utctimetuple())) or False
    except ValueError:
      # provided string does not match our expected format.
      return False

  def getTopicInfoFromListing(self, text):
    """
    Returns a dict of topic attributes from a chunk of a topic list, or False if it doesn't match a topic listing regex.
    """
    # thisTopic = re.search(r'\<td\ class\=\"oh\"\>\<div\ class\=\"fl\"\>((?P<closed><span\ class\=\"closed\"\>))?\<a\ href\=\"//[a-z]+\.endoftheinter\.net/showmessages\.php\?topic\=(?P<topicID>[0-9]+)\">(<b>)?(?P<title>[^<]+)(</b>)?\</a\>(</span>)?</div\>\<div\ class\=\"fr\"\>(?P<tags>(.+?))?\ \<\/div\></td\>\<td\>\<a\ href\=\"//endoftheinter\.net/profile\.php\?user=(?P<userID>[0-9]+)\"\>(?P<username>[^<]+)\</a\>\</td\>\<td\>(?P<postCount>[0-9]+)(\<span id\=\"u[0-9]+_[0-9]+\"\> \(\<a href\=\"//(boards)?(archives)?\.endoftheinter\.net/showmessages\.php\?topic\=[0-9]+(\&amp\;page\=[0-9]+)?\#m[0-9]+\"\>\+(?P<newPostCount>[0-9]+)\</a\>\)\&nbsp\;\<a href\=\"\#\" onclick\=\"return clearBookmark\([0-9]+\, \$\(\&quot\;u[0-9]+\_[0-9]+\&quot\;\)\)\"\>x\</a\>\</span\>)?\</td\>\<td\>(?P<lastPostTime>[^>]+)\</td\>', text)
    thisTopic = re.search(r'\<td\ class\=\"oh\"\>\<div\ class\=\"fl\"\>((?P<closed><span\ class\=\"closed\"\>))?\<a\ href\=\"//[a-z]+\.endoftheinter\.net/showmessages\.php\?topic\=(?P<topicID>[0-9]+)\">(<b>)?(?P<title>[^<]+)(</b>)?\</a\>(</span>)?</div\>\<div\ class\=\"fr\"\>((?P<tags>(.+?))\ )?\<\/div\></td\>\<td\>(\<a\ href\=\"//endoftheinter\.net/profile\.php\?user=(?P<userID>[0-9]+)\"\>(?P<username>[^<]+)\</a\>)?(Human)?\</td\>\<td\>(?P<postCount>[0-9]+)(\<span id\=\"u[0-9]+_[0-9]+\"\> \(\<a href\=\"//(boards)?(archives)?\.endoftheinter\.net/showmessages\.php\?topic\=[0-9]+(\&amp\;page\=[0-9]+)?\#m[0-9]+\"\>\+(?P<newPostCount>[0-9]+)\</a\>\)\&nbsp\;\<a href\=\"\#\" onclick\=\"return clearBookmark\([0-9]+\, \$\(\&quot\;u[0-9]+\_[0-9]+\&quot\;\)\)\"\>x\</a\>\</span\>)?\</td\>\<td\>(?P<lastPostTime>[^>]+)\</td\>', text)
    if thisTopic:
      user = {'userID': 0, 'username': 'Human'}
      if thisTopic.group('userID') and thisTopic.group('username'):
        user['userID'] = int(thisTopic.group('userID'))
        user['username'] = thisTopic.group('username')
      newPostCount = 0
      if thisTopic.group('newPostCount'):
        newPostCount = int(thisTopic.group('newPostCount'))
      closedTopic = False
      if thisTopic.group('closed'):
        closedTopic = True
      if thisTopic.group('tags'):
        tags = [re.search(r'\"\>(?P<name>[^<]+)', tag).group('name') for tag in thisTopic.group('tags').split("</a>") if tag]
      else:
        tags = []
      return dict([('topicID', int(thisTopic.group('topicID'))), ('title', thisTopic.group('title')), ('userID', user['userID']), ('username', user['username']), ('postCount', int(thisTopic.group('postCount'))), ('newPostCount', newPostCount), ('lastPostTime', thisTopic.group('lastPostTime')), ('closed', closedTopic), ('tags', tags)])
    else:
      return False

  def getTopicList(self, allowedTags=[], forbiddenTags=[], maxTopicTime="", maxTopicID="", topicsActiveSince=False, topics=False, recurse=False):
    """
    Special case of searchTopics. Only fetches latest page of topics by default.
    """
    if not topics:
      topics = []
    return self.searchTopics(query="", allowedTags=allowedTags, forbiddenTags=forbiddenTags, maxTopicTime=maxTopicTime, maxTopicID=maxTopicID, topicsActiveSince=topicsActiveSince, topics=topics, recurse=recurse)
   
  def appendTopicSearchTopics(self, text, url, curlHandle, paramArray):
    """
    Takes the result of a pyparallelcurl request on a topic search and appends the resultant topics to the given list.
    """
    topics = paramArray[0]
    
    if not self.checkPageAuthed(text):
      if self.reauthenticate():
        self.parallelCurl.startrequest(url, self.appendTopicSearchTopics, paramArray)
        return
    
    # split the topic listing string into a list so that one topic is in each element.
    topicListingHTML = self.getEnclosedString(text, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
    if not topicListingHTML:
      return False
    topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []

    for topic in topicListingHTML:
      topicInfo = self.getTopicInfoFromListing(topic)
      if topicInfo:
        topics.append(topicInfo)
  
  def formatTagQueryString(self, allowedTags=[], forbiddenTags=[]):
    """
    Takes a list of tag names.
    Returns a string formatted for ETI's topic search URL.
    E.g. "Posted-Anonymous+Starcraft+Programming"
    """
    if len(forbiddenTags) > 0:
      return "-".join(["+".join(allowedTags), "-".join(forbiddenTags)])
    else:
      return "+".join(allowedTags)

  def searchTopics(self, query="", allowedTags=[], forbiddenTags=[], maxTopicTime="", maxTopicID="", topicsActiveSince=False, topics=False, recurse=True):
    """
    Searches for topics using given parameters, and returns a list of dicts of returned topics.
    By default, recursively iterates through every page of search results.
    Upon failure returns False.
    """
    if not topics:
      topics = []
    
    # check to see if we need to request a page.
    if topicsActiveSince and maxTopicTime and maxTopicTime <= topicsActiveSince:
      return topics
    
    # assemble the search query and request this search page's topic listing.
    searchQuery = urllib.urlencode([('q', str(query)), ('ts', str(maxTopicTime)), ('t', str(maxTopicID))])
    topicPageHTML = self.getPage('http://boards.endoftheinter.net/topics/' + self.formatTagQueryString(allowedTags=allowedTags, forbiddenTags=forbiddenTags) + '?' + searchQuery)
    
    # split the topic listing string into a list so that one topic is in each element.
    topicListingHTML = self.getEnclosedString(topicPageHTML, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
    if not topicListingHTML:
      return topics
    topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []
    
    originalTopicsNum = len(topics)
    for topic in topicListingHTML:
      topicInfo = self.getTopicInfoFromListing(topic)
      if topicInfo and (not topicsActiveSince or self.getTopicDateUnix(topicInfo['lastPostTime']) > topicsActiveSince):
        topics.append(topicInfo)
    
    if len(topics) == originalTopicsNum:
      return topics

    if not recurse:
      return True and topics or False
    # we can't parallelize this, since we have no way of predicting the next ts and t parameters.
    return True and self.searchTopics(query=query, maxTopicTime=self.getTopicDateUnix(topics[-1]['lastPostTime']), maxTopicID=topics[-1]['topicID'], topicsActiveSince=topicsActiveSince, topics=topics, recurse=recurse) or False
    
  def checkTopicValid(self, text):
    """
    Given the HTML of a topic page, checks to ensure that the topic exists and that we can read it.
    """
    #return not bool(re.search(r'<em>Invalid topic.</em>', text)) and not bool(re.search(r'<h1>500 - Internal Server Error</h1>', text)) and not bool(re.search(r'<em>You are not authorized to view messages on this board.</em>', text))
    return bool(re.search(r'Page\ 1\ of\ ',str(text)))

  def checkArchivedTopic(self, text):
    """
    Given the HTML of a topic page, checks to see if this is an archived topic.
    """
    return bool(re.search(r'<h2><em>This topic has been archived\. No additional messages may be posted\.</em></h2>', text))

  def checkArchivedRedirect(self, text):
    """
    Given the HTML of a topic header, checks to see if this is redirecting to an archived topic.
    """
    return bool(re.search(r'HTTP\/1\.1 302 Moved Temporarily', text))
    # return bool(re.search(r'\<meta\ http\-equiv\=\"refresh\"\ content\=\"0\;url\=//archives\.endoftheinter\.net/showmessages\.php\?', text))

  def getTopicID(self, text):
    """
    Given the HTML of a topic's page, return topic ID or False if not found.
    """
    return True and int(self.getEnclosedString(text, r'showmessages\.php\?topic\=', r'[^\d]')) or False
    
  def getTopicTitle(self, text):
    """
    Given the HTML of a topic's page, return topic title or False if not found.
    """
    return True and self.getEnclosedString(text, r'\<\/div\>\<h1\>', r'\<\/h1\>') or False
    
  def getPostID(self, text):
    """
    Given HTML of a post within a topic, return post ID or False if not found.
    """
    return True and int(self.getEnclosedString(text, r'<div class="message-container" id="m', r'">')) or False

  def getPostUsername(self, text):
    """
    Given HTML of a post, return poster's username or False if not found.
    """
    return True and self.getEnclosedString(text, r'<b>From:</b>\ <a href="//endoftheinter\.net/profile\.php\?user=\d+">', r'</a>') or False

  def getPostUserID(self, text):
    """
    Given HTML of a post, return poster's userID or False if not found.
    """
    return True and int(self.getEnclosedString(text, r'<b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">')) or False

  def getPostDate(self, text):
    """
    Given HTML of a post, return post date as a string or False if not found.
    """
    return True and self.getEnclosedString(text, r'<b>Posted:</b> ', r' \| ') or False

  def getPostDateUnix(self, text):
    """
    Given HTML of a post, return post date as a unix timestamp or False if not found.
    """
    if self.getPostDate(text):
      return True and int(calendar.timegm(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getPostDate(text), "%m/%d/%Y %I:%M:%S %p")).utctimetuple()))
      #return True and int(time.mktime(pytz.timezone("US/Central").localize(datetime.datetime.strptime(self.getPostDate(text), "%m/%d/%Y %I:%M:%S %p")).astimezone(self.timezone).timetuple())) or False
    else:
      return False
  
  def getPostSig(self, text):
    """
    Given HTML of a post, return sig or False if not found.
    """
    return True and (True and self.getEnclosedString(text, r'---<br />', r'</td>', multiLine=True, greedy=False) or "") or False
  
  def getPostText(self, text):
    """
    Given HTML of a post, return post text stripped of sig or False if not found.
    """  
    return True and (True and self.getEnclosedString(text, r' class="message">', r'---<br />', multiLine=True, greedy=True) or self.getEnclosedString(text, r' class="message">', r'</td>', multiLine=True, greedy=True)) or False

  def getTopicPageNum(self, text):
    """
    Given a page in a topic, returns the current page number.
    """
    return True and int(self.getEnclosedString(text, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page ', r' of')) or False
    
  def getTopicNumPages(self, text):
    """
    Given a page in a topic, returns the number of pages in this topic.
    """
    return True and int(self.getEnclosedString(text, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page \d+ of <span>', r'</span>')) or False
    
  def getPagePosts(self, text):
    """
    Takes the HTML of one page of a topic or link and returns a list containing the HTML for one post in each element on said page.
    """
    return text.split('</td></tr></table></div>')[:-1]
    
  def getLatestTopicID(self, text):
    """
    Takes the HTML of a topic listing and returns the largest topicID on this page.
    Returns False if no topicIDs on this page.
    """
    latestTopic = self.getTopicInfoFromListing(text)
    if latestTopic:
      return int(latestTopic['topicID'])
    else:
      return False

  def getActiveTags(self):
    """
    Returns a list of the names of the active tags at the moment.
    """
    mainPage = self.getPage("https://endoftheinter.net/main.php")
    tagLinksHTML = self.getEnclosedString(mainPage, '<div style\="font\-size\: 14px">', '</div>', multiLine=True)
    tagLinks = tagLinksHTML.split('&nbsp;&bull; ')
    return [self.getEnclosedString(text, '">', '</a>').strip() for text in tagLinks]

  def getTagInfo(self, name):
    """
    Takes the name of a tag and returns all the information that the currently signed-in user can view about it.
    """
    tagInfoParams = urllib.urlencode([('e', ''), ('q', str(name).replace(" ", "_")), ('n', '1')])
    tagInfoPage = self.getPage("https://boards.endoftheinter.net/async-tag-query.php?" + tagInfoParams)
    tagInfoPage = tagInfoPage[1:]
    try:
      tagJSON = json.loads(tagInfoPage)
    except ValueError:
      print "Warning: invalid JSON object provided by ETI ajax tag interface."
      raise
    if len(tagJSON) < 1:
      return False
    tagJSON = tagJSON[0]
    tag = {'name': tagJSON[0]}

    tag['staff'] = []

    moderatorText = self.getEnclosedString(tagJSON[1][0], "<b>Moderators: </b>", "<br /><b>Administrators:")
    if moderatorText:
      descriptionEndTag = "<br /><b>Moderators:"
      moderatorTags = moderatorText.split(", ")
      for moderator in moderatorTags:
        tag['staff'].append({'username': str(self.getEnclosedString(moderator, '\">', "</a>")), 'id': int(self.getEnclosedString(moderator, "\?user\=", '\">')), 'role':'moderator'})
    else:
      descriptionEndTag = "<br /><b>Administrators:"

    administratorText = self.getEnclosedString(tagJSON[1][0], startString="<br /><b>Administrators: </b>", greedy=True)
    if administratorText:
      administratorTags = administratorText.split(", ")
      for administrator in administratorTags:
        tag['staff'].append({'username': str(self.getEnclosedString(administrator, '\">', "</a>")), 'id': int(self.getEnclosedString(administrator, "\?user\=", '\">')), 'role':'administrator'})
    descriptionText = self.getEnclosedString(tagJSON[1][0], ":</b> ", descriptionEndTag)
    if descriptionText:
      tag['description'] = descriptionText
    else:
      tag['description'] = ''

    tagInteractions = tagJSON[1][1]
    tag['related_tags'] = tag['forbidden_tags'] = tag['dependent_tags'] = []
    if len(tagInteractions) > 0:
      if '0' in tagInteractions:
         tag['forbidden_tags'] = tagInteractions['0'].keys()
      if '1' in tagInteractions:
         tag['dependent_tags'] = tagInteractions['1'].keys()
      if '2' in tagInteractions:
         tag['related_tags'] = tagInteractions['2'].keys()
    return tag
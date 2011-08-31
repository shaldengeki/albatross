#!/usr/bin/python
# Copyright 2010 Shal Dengeki
# Licensed under the WTF Public License, Version 2.0
# http://sam.zoy.org/wtfpl/COPYING
# Provides link- and board-scraping functions for ETI.

import os
import re
import sys
import urllib
import urllib2
import time
import datetime
import pycurl
import pyparallelcurl
import cStringIO
from xml.etree import ElementTree

def printUsageAndQuit():
  """
  Prints usage information and exits.
  """
  print "usage: [--report-links] [--num-requests n] username password startID endID";
  sys.exit(1)

def parseCookieHeader(string):
  """
  Given a cookie response header returned by pyCurl, return an array of cookie key/values.
  """
  
  string_array = string.split("\r\n")
  cookieList = []
  for line in string_array:
    if line.startswith("Set-Cookie:"):
      cookieList.append('='.join(line[11:-1].strip().split(";")[0].split("=")))
      
  cookieString = '; '.join(cookieList)
  
  return cookieString

def login(username, password):
  """
  Logs into LL using the provided username and password, returning the resultant cookie string.
  """
  response = cStringIO.StringIO()
  loginHeaders = pycurl.Curl()
  
  loginHeaders.setopt(pycurl.SSL_VERIFYPEER, False)
  loginHeaders.setopt(pycurl.SSL_VERIFYHOST, False)
  loginHeaders.setopt(pycurl.POST, 1)
  loginHeaders.setopt(pycurl.HEADER, True)
  loginHeaders.setopt(pycurl.POSTFIELDS, urllib.urlencode(dict([('b',username), ('p', password), ('r', '')])))
  loginHeaders.setopt(pycurl.URL, 'https://endoftheinter.net/index.php')
  loginHeaders.setopt(pycurl.USERAGENT, 'Albatross')
  loginHeaders.setopt(pycurl.WRITEFUNCTION, response.write)
  
  loginHeaders.perform()
  loginHeaders.close()
  
  cookieHeader = response.getvalue()
  
  if re.search(r'Sie bitte 15 Minuten', cookieHeader) or not re.search(r'session=', cookieHeader):
    return False

  cookieString = parseCookieHeader(cookieHeader)
  return cookieString

def getEnclosedString(text, startString='', endString='', multiLine=False):
  """
  Given some text and two strings, return the string that is encapsulated by the first sequence of these two strings in order.
  If either string is not found or text is empty, return false.
  Multiline option makes the return possibly multi-line.
  """
  if not text or not len(text):
    return False
  if multiLine:
    stringMatch = re.search(startString + r'(?P<return>.+?)' + endString, text, flags=re.DOTALL)
  else:
    stringMatch = re.search(startString + r'(?P<return>.+?)' + endString, text)  
  if not stringMatch:
    return False
  return stringMatch.group('return')

def getPage(url, cookieString='', retries=10):
  """
  Uses cURL to read a page.
  Retries up to retries times before returning an error.
  """
  
  for x in range(retries): # Always limit number of retries. For now just return the first request.
    response = cStringIO.StringIO()
    pageRequest = pycurl.Curl()
    
    pageRequest.setopt(pycurl.SSL_VERIFYPEER, False)
    pageRequest.setopt(pycurl.SSL_VERIFYHOST, False)
    pageRequest.setopt(pycurl.URL, url)
    pageRequest.setopt(pycurl.USERAGENT, 'Albatross')
    pageRequest.setopt(pycurl.COOKIE, cookieString)
    pageRequest.setopt(pycurl.WRITEFUNCTION, response.write)
    pageRequest.perform()
    pageRequest.close()
    
    response = response.getvalue()
    return response
    
  return False
  
def getLinkPage(linkID, cookieString):
  """
  Grabs a link's page, given its linkID and a cookie string, and returns the HTML.
  Upon failure returns False.
  """
  linkPage = pycurl.Curl()
  response = cStringIO.StringIO()
  linkPage.setopt(pycurl.COOKIE, cookieString)
  linkPage.setopt(pycurl.URL, 'https://links.endoftheinter.net/linkme.php?l=' + str(linkID))
  linkPage.setopt(pycurl.USERAGENT, 'Albatross')
  linkPage.setopt(pycurl.SSL_VERIFYPEER, False)
  linkPage.setopt(pycurl.SSL_VERIFYHOST, False)
  linkPage.setopt(pycurl.WRITEFUNCTION, response.write)
  linkPage.perform()
  linkPage.close()
  
  linkPageHTML = response.getvalue()
  return True and linkPageHTML or False
  
def getLinkTitle(text):
  """
  Given HTML of a link page, return link title or False if title not found.
  """
  return getEnclosedString(text, '<h1>', '</h1>')

def getLinkLink(text):
  """
  Given HTML of a link page, return link field of link.
  """
  return getEnclosedString(text, ' target="_blank">', '</a>')
  
def getLinkCreator(text):
  """
  Given HTML of a link page, returns a dict with userid and username of user who created this link.
  """
  creatorText = getEnclosedString(text, r'\<b\>Added by\:\<\/b\> \<a href\=\"profile\.php\?user\=', r'\<\/a\>\<br \/\>')
  if not creatorText:
    return False
  else:
    creatorList = creatorText.split('">')
    return dict([('userid', creatorList[0]), ('username', creatorList[1])])

def getLinkDate(text):
  """
  Given HTML of a link page, returns the date it was added.
  """
  return getEnclosedString(text, '<b>Date:</b> ', '<br />')
  
def getLinkCode(text):
  """
  Given HTML of a link page, returns the link code.
  """
  return getEnclosedString(text, r'\<b\>Code:\<\/b\> \<a href\=\"linkme\.php\?l\=\d+\"\>', r'</a><br />')

def getLinkHits(text):
  """
  Given HTML of a link page, returns the number of hits on this link.
  """
  hitText = getEnclosedString(text, '<b>Hits:</b> ', r'<br />')
  return True and int(hitText) or False

def getLinkRating(text):
  """
  Given HTML of a link page, returns the rating of this link.
  """
  ratingText = getEnclosedString(text, '<b>Rating:</b> ', r'/10')
  return True and float(ratingText) or False

def getLinkVotes(text):
  """
  Given HTML of a link page, returns the number of votes on this link.
  """
  votesText = getEnclosedString(text, r'\/10 \(based on ', r' votes\)\<br \/\>')
  return True and int(votesText) or False

def getLinkRank(text):
  """
  Given HTML of a link page, returns this link's rank.
  """
  rankText = getEnclosedString(text, r'<b>Rank:</b> ', r'<br/>')
  return True and int(rankText) or False

def getLinkCategories(text):
  """
  Given HTML of a link page, returns list of link categories.
  """
  categoryText = getEnclosedString(text, '<b>Categories:</b> ', '<br />')
  if not categoryText:
    return False
  else:
    return categoryText.split(', ')

def getLinkDescription(text):
  """
  Given HTML of a link page, returns the link description.
  """
  return getEnclosedString(text, '<b>Description:</b>\s+', '  <br /><br />')

def reportLink(cookieString, linkID, reason, comments):
  """
  Reports linkID for specified reason and appends comments.
  """
  if not cookieString or not int(linkID) or not int(reason) or not len(comments):
    return False
  params = urllib.urlencode(dict([('r', int(reason)), ('c', comments)]))
  report_link = opener.open('https://links.endoftheinter.net/linkreport.php?l='+str(int(linkID)), params)
  data = report_link.read()
  report_link.close()
# LL doesn't provide any feedback upon reporting a link so we have to assume that all went well.
  return True
  
def checkLinkDeleted(text):
  """
  Returns True if link has been deleted; False if it hasn't.
  """
  deletedMatch = re.search(r'\<em\>This link has been deleted, and is no longer available\<\/em\>', text)
  return bool(deletedMatch)
  
def checkLinkExists(text):
  """
  Checks if the selected link is not deleted and is a valid link (i.e. not out-of-bounds).
  Returns True or False to reflect if link exists.
  """
  invalid_match = re.search(r'\<em\>Invalid link\!\<\/em\>', text)
  return (not invalid_match and not checkLinkDeleted(text))
  
def checkLinkNeedsReporting(text, url, curlHandle, paramArray):
  """
  Checks to see if a link needs to be reported.
  Checks several things:
  1.  If there are [TAGS] in the title, checks to ensure categories are properly set for those tags.
  2.  If there are links to sites specified by site_dict within the link description or actual link, 
      checks those to see if they're down and if this link is tagged with the 'Uploads' category.
  Returns False if all the checks pass (or the link is deleted), a list of reasons if not.
  """
  global parallelCurl
  
  if not checkLinkExists(text):
    return False

  if checkLinkDeleted(text):
    return False
  
  linkID = paramArray[0]
  startID = paramArray[1]
  endID = paramArray[2]
  tag_dict = paramArray[3]
  site_dict = paramArray[4]
  cookieString = paramArray[5]
  
  reasonList = []
  
  # check to make sure that any [TAGS] in the title are properly-reflected in the categories.
  title = getLinkTitle(text)
  title_tags = re.findall(r'\[\S+?\]', title)
  categories = getLinkCategories(text)
  for tag in title_tags:
    if tag.upper() in tag_dict:
      for required_tag in tag_dict[tag.upper()]:
        if categories and required_tag not in categories:
          reasonList.append((3, 'Needs category: ' + required_tag))
  
  # check link's link and description to see if there are links to popular upload sites.
  link = getLinkLink(text)
  if link:
    link_match = re.search(r'(\w+\.com)', link)
    if link_match and link_match.groups()[0] in site_dict:
      base_url = link_match.groups()[0]
      link_external_site = urllib2.urlopen(link)
      site_text = link_external_site.read()
      link_external_site.close()
      if site_dict[base_url] in site_text:
        reasonList.append((2, 'Dead link.'))
  else:
    link = ''
  # if there are upload links in the link or description and this link isn't tagged as upload, flag this link to be reported.
  description = getLinkDescription(text)
  if description:
    allText_matches = re.findall(r'(\w+\.com)', str(link) + str(description))
    if allText_matches:
      for base_url in allText_matches:
        if base_url in site_dict and 'Uploads' not in categories:
            reasonList.append((3, 'Needs category: Uploads'))

  if reasonList:
    reportComment = ""
    for tuple in reasonList:
      if not reportComment:
        reportComment = tuple[1]
      else:
        reportComment = reportComment + "\r\n" + tuple[1]
      lastReason = tuple[0]
    if cookieString and int(linkID) and int(lastReason) and len(reportComment):
      parallelCurl.startrequest('https://links.endoftheinter.net/linkreport.php?l='+str(int(linkID)), reportLink, [], post_fields = urllib.urlencode(dict([('r', int(lastReason)), ('c', reportComment)])))
    print "Reported",
    print "linkID " + str(linkID) + " (type " + str(lastReason) + "): " + ", ".join(reportComment.split("\r\n"))
  # waiting sucks.
  if linkID % 100 == 0:
    print "Progress: " + str(round(100*(linkID - startID)/(endID - startID), 2)) + "% (" + str(linkID) + "/" + str(endID) + ")"

def reportLinks(startID, endID, num_concurrent_requests, cookieString):
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
  curl_options = {
    pycurl.SSL_VERIFYPEER: False,
    pycurl.SSL_VERIFYHOST: False,
    pycurl.FOLLOWLOCATION: True, 
    pycurl.COOKIE: cookieString
  }
  parallelCurl = pyparallelcurl.ParallelCurl(num_concurrent_requests, curl_options)

  for linkID in range(startID, endID):
    parallelCurl.startrequest('https://links.endoftheinter.net/linkme.php?l='+str(linkID), checkLinkNeedsReporting, [linkID, startID, endID, tag_dict, site_dict, cookieString])

  parallelCurl.finishallrequests()

def getTopicPage(cookieString, topicID, boardID=42, pageNum=1, archived=False, userID=""):
  """
  Grabs a topic's message listing, given its topicID and a cookie string (and optional boardID, userID, archived, and page number parameters), and returns the HTML.
  Upon failure returns False.
  """
  if not archived:
    subdomain = "boards"
  else:
    subdomain = "archives"  
  
  topicPage = pycurl.Curl()
  response = cStringIO.StringIO()
  topicPage.setopt(pycurl.COOKIE, cookieString)  
  topicPage.setopt(pycurl.URL, 'https://' + subdomain + '.endoftheinter.net/showmessages.php?board=' + str(boardID) + '&topic=' + str(topicID) + '&u=' + str(userID) + '&page=' + str(pageNum))
  topicPage.setopt(pycurl.SSL_VERIFYPEER, False)
  topicPage.setopt(pycurl.SSL_VERIFYHOST, False)
  topicPage.setopt(pycurl.WRITEFUNCTION, response.write)
  topicPage.perform()
  topicPage.close()
  
  topicPageHTML = response.getvalue()
  return True and topicPageHTML or False

def getTopicInfoFromListing(text):
  """
  Returns a dict of topic attributes from a chunk of a topic list, or False if it doesn't match a topic listing regex.
  """
  thisTopic = re.search(r'\<a href\=\"//[a-z]+\.endoftheinter\.net/showmessages\.php\?board\=(?P<boardID>[0-9]+)\&amp\;topic\=(?P<topicID>[0-9]+)\">(\<b\>)?(?P<title>[^<]+)(\</b\>)?\</a\>(\</span\>)?\</td\>\<td\>\<a href\=\"//endoftheinter.net/profile\.php\?user=(?P<userID>[0-9]+)\"\>(?P<username>[^<]+)\</a\>\</td\>\<td\>(?P<postCount>[0-9]+)(\<span id\=\"u[0-9]+_[0-9]+\"\> \(\<a href\=\"//(boards)?(archives)?\.endoftheinter\.net/showmessages\.php\?board\=[0-9]+\&amp\;topic\=[0-9]+(\&amp\;page\=[0-9]+)?\#m[0-9]+\"\>\+(?P<newPostCount>[0-9]+)\</a\>\)\&nbsp\;\<a href\=\"\#\" onclick\=\"return clearBookmark\([0-9]+\, \$\(\&quot\;u[0-9]+\_[0-9]+\&quot\;\)\)\"\>x\</a\>\</span\>)?\</td\>\<td\>(?P<lastPostTime>[^>]+)\</td\>', text)
  if thisTopic:
    newPostCount = 0
    if thisTopic.group('newPostCount'):
      newPostCount = int(thisTopic.group('newPostCount'))
    return dict([('boardID', int(thisTopic.group('boardID'))), ('topicID', int(thisTopic.group('topicID'))), ('title', thisTopic.group('title')), ('userID', int(thisTopic.group('userID'))), ('username', thisTopic.group('username')), ('postCount', int(thisTopic.group('postCount'))), ('newPostCount', newPostCount), ('lastPostTime', thisTopic.group('lastPostTime'))])
  else:
    return False

def getTopicList(cookieString, archived=False, boardID=42, pageNum=1, topics=[], recurse=False):
  """
  Returns a list of topic info dicts for the given board and page number.
  By default, does not recurse through every page.
  Upon failure returns False.
  """
  if not archived:
    subdomain = "boards"
  else:
    subdomain = "archives"
  
  # assemble the search query and request this search page's topic listing.
  searchQuery = urllib.urlencode([('board', boardID), ('page', pageNum)])
  topicPageHTML = getPage('https://' + subdomain + '.endoftheinter.net/showtopics.php?' + searchQuery, cookieString)
  
  # get the total page number.
  totalPageNum = getTopicNumPages(topicPageHTML)
  
  # split the topic listing string into a list so that one topic is in each element.
  topicListingHTML = getEnclosedString(topicPageHTML, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
  topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []
  
  for topic in topicListingHTML:
    topicInfo = getTopicInfoFromListing(topic)
    if topicInfo:
      topics.append(topicInfo)
    else:
      return False

  # if there are still more pages in the search results and user has not specified otherwise, then recurse.
  if pageNum < totalPageNum and recurse:
    return getTopicList(cookieString, archived=archived, boardID=boardID, pageNum=pageNum+1, topics=topics, recurse=True)
  else:
    return True and topics or False
 
def searchTopics(cookieString, archived=False, boardID=42, allWords="", exactPhrase="", atLeastOne="", without="", numPostsMoreThan=0, numPostsCount='', timeCreatedWithin=1, timeCreatedTime='', timeCreatedUnit=86400, lastPostWithin=1, lastPostTime=0, lastPostUnit=86400, pageNum=1, topics=[], recurse=True):
  """
  Searches for topics using given parameters, and returns a list of dicts of returned topics.
  By default, recursively iterates through every page of search results.
  Upon failure returns False.
  """
  if not archived:
    subdomain = "boards"
  else:
    subdomain = "archives"
  
  # assemble the search query and request this search page's topic listing.
  searchQuery = urllib.urlencode([('s_aw', allWords), ('s_ep', exactPhrase), ('s_ao', atLeastOne), ('s_wo', without), ('m_t', numPostsMoreThan), ('m_f', numPostsCount), ('t_t', timeCreatedWithin), ('t_f', timeCreatedTime), ('t_m', timeCreatedUnit), ('l_t', lastPostWithin), ('l_f', lastPostTime), ('l_m', lastPostUnit), ('board', boardID), ('page', pageNum)]).replace('%2A', '*')
  topicPageHTML = getPage('https://' + subdomain + '.endoftheinter.net/search.php?' + searchQuery + '&submit=Search', cookieString)
  
  # get the total page number.
  totalPageNum = getTopicNumPages(topicPageHTML)

  # split the topic listing string into a list so that one topic is in each element.
  topicListingHTML = getEnclosedString(topicPageHTML, '<th>Last Post</th></tr>', '</tr></table>', multiLine=True)
  topicListingHTML = topicListingHTML.split('</tr>') if topicListingHTML else []
  
  for topic in topicListingHTML:
    topicInfo = getTopicInfoFromListing(topic)
    if topicInfo:
      topics.append(topicInfo)
    else:
      return False

  # if there are still more pages in the search results and user has not specified otherwise, then recurse.
  if pageNum < totalPageNum and recurse:
    return searchTopics(cookieString, archived=archived, boardID=boardID, allWords=allWords, exactPhrase=exactPhrase, atLeastOne=atLeastOne, without=without, numPostsMoreThan=numPostsMoreThan, numPostsCount=numPostsCount, timeCreatedWithin=timeCreatedWithin, timeCreatedTime=timeCreatedTime, timeCreatedUnit=timeCreatedUnit, lastPostWithin=lastPostWithin, lastPostTime=lastPostTime, lastPostUnit=lastPostUnit, pageNum=pageNum+1, topics=topics)
  else:
    return True and topics or False
  
def checkTopicValid(text):
  """
  Given the HTML of a topic page, checks to ensure that the topic exists and that we can read it.
  """
  #return not bool(re.search(r'<em>Invalid topic.</em>', text)) and not bool(re.search(r'<h1>500 - Internal Server Error</h1>', text)) and not bool(re.search(r'<em>You are not authorized to view messages on this board.</em>', text))
  return bool(re.search(r'<h2>',text))

def checkArchivedTopic(text):
  """
  Given the HTML of a topic page, checks to see if this is an archived topic.
  """
  return bool(re.search(r'<h2><em>This topic has been archived\. No additional messages may be posted\.</em></h2>', text))

def checkArchivedRedirect(text):
  """
  Given the HTML of a topic page, checks to see if this is redirecting to an archived topic.
  """
  return bool(re.search(r'<meta http-equiv="refresh" content="0;url=//archives\.endoftheinter\.net/showmessages\.php\?', text))

def getBoardID(text):
  """
  Given the HTML of a topic page, returns the board it's on.
  """
  return True and int(getEnclosedString(text, r'\w\.endoftheinter\.net/showmessages\.php\?board\=', r'[^-\d]')) or False
  
def getTopicID(text):
  """
  Given the HTML of a topic's page, return topic ID or False if not found.
  """
  return True and int(getEnclosedString(text, r'showmessages\.php\?board=[-\d]+\&amp\;topic\=', r'[^\d]')) or False
  
def getPostID(text):
  """
  Given HTML of a post within a topic, return post ID or False if not found.
  """
  return True and int(getEnclosedString(text, r'<div class="message-container" id="m', r'">')) or False

def getPostUsername(text):
  """
  Given HTML of a post, return poster's username or False if not found.
  """
  return True and getEnclosedString(text, r'<b>From:</b>\ <a href="//endoftheinter\.net/profile\.php\?user=\d+">', r'</a>') or False

def getPostUserID(text):
  """
  Given HTML of a post, return poster's userID or False if not found.
  """
  return True and int(getEnclosedString(text, r'<b>From:</b> <a href="//endoftheinter\.net/profile\.php\?user=', r'">')) or False

def getPostDate(text):
  """
  Given HTML of a post, return post date as a string or False if not found.
  """
  return True and getEnclosedString(text, r'<b>Posted:</b> ', r' \| ') or False

def getPostDateUnix(text):
  """
  Given HTML of a post, return post date as a unix timestamp or False if not found.
  """
  if getPostDate(text):
    return True and int(time.mktime(datetime.datetime.strptime(getPostDate(text), "%m/%d/%Y %I:%M:%S %p").timetuple())) or False
  else:
    return False

def getPostText(text):
  """
  Given HTML of a post, return post text stripped of sig or False if not found.
  """  
  return True and (True and getEnclosedString(text, r' class="message">', r'---<br />', multiLine=True) or getEnclosedString(text, r' class="message">', r'</td>', multiLine=True)) or False

def getTopicPageNum(text):
  """
  Given a page in a topic, returns the current page number.
  """
  return True and int(getEnclosedString(text, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page ', r' of')) or False
  
def getTopicNumPages(text):
  """
  Given a page in a topic, returns the number of pages in this topic.
  """
  return True and int(getEnclosedString(text, r'">(First Page</a> \| )?(<a href)?(\S+)?(Previous Page</a> \| )?Page \d+ of <span>', r'</span>')) or False
  
def getTopicPosts(text):
  """
  Takes the HTML of one page of a topic and returns a list of the posts on said page.
  """
  return text.split('</div></td></tr></table></div>')[:-1]
  
def getLatestTopicID(text):
  """
  Takes the HTML of a topic listing and returns the largest topicID on this page.
  Returns False if no topicIDs on this page.
  """
  sortedTopicIDs = sorted(re.findall(r'<tr><td><a href="//boards\.endoftheinter\.net/showmessages\.php\?board=42&amp;topic=(\d+)">', text))
  if sortedTopicIDs and len(sortedTopicIDs) > 0:
    return int(sortedTopicIDs[-1])
  else:
    return False
    
def main():
  global parallelCurl
  
  args = sys.argv[1:]
  if not args or len(args) < 4:
    printUsageAndQuit()

  report_links = False
  if args[0] == "--report-links":
    report_links = True
    del args[0]

  num_concurrent_requests = 20
  if args[0] == "--num-requests":
    num_concurrent_requests = int(args[1])
    del args[0:2]
    
  llUsername = str(args[0])
  llPassword = str(args[1])
  startID = int(args[2])
  endID = int(args[3])

  cookieString = login(llUsername, llPassword)
  if not cookieString:
    print "Unable to log in with provided credentials."
    sys.exit(1)
    
  if report_links:
    reportLinks(startID, endID, num_concurrent_requests, cookieString)

if __name__ == '__main__':
  main()
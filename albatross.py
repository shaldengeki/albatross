#!/usr/bin/python
# Copyright 2010 Shal Dengeki
# Licensed under the WTF Public License, Version 2.0
# http://sam.zoy.org/wtfpl/COPYING
# Monitors and reports malformed links on endoftheinter.net

import os
import re
import sys
import urllib
import urllib2

def login(username, password):
  """
  Logs into LL using the provided username and password, returning the resultant opener.
  """
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
  urllib2.install_opener(opener)

  params = urllib.urlencode(dict([('b', username), ('p', password)]))
  login_page = opener.open('https://endoftheinter.net', params)
  data = login_page.read()
  login_page.close()
  loggedin_match = re.search(r'\<h1\>End of the Internet\<\/h1\>', data)
  if loggedin_match:
    return opener
  else:
    return False

def test(got, expected):
  """ 
  Simple provided test() function used in main() to print
  what each function returns vs. what it's supposed to return.
  """
  if got == expected:
    prefix = ' OK '
  else:
    prefix = '  X '
  print '%s got: %s expected: %s' % (prefix, repr(got), repr(expected))

def runTests(opener):
  """
  Runs tests on expected results from getLink____() functions on a preset LL link.
  """
  link_page = opener.open('http://links.endoftheinter.net/linkme.php?l=18')
  data = link_page.read()
  link_page.close()
  print "Tests:"
  print "getLinkTitle"
  test(getLinkTitle(data), 'I believe you have my stapler')
  print 
  
  print "getEnclosedString"
  test(getEnclosedString(data, 'aspdfasdpofijas', 'apsdijfpasodjf'), '')  
  test(getEnclosedString(data, '<h1>', '</h1>'), 'I believe you have my stapler')
  print
  
  print "getLinkLink"
  test(getLinkLink(data), 'http://stapler.ytmnd.com/')
  print

  print "getLinkCreator"
  test(getLinkCreator(data), dict([('userid', '1'), ('username', 'LlamaGuy')]))
  print

  print "getLinkDate"
  test(getLinkDate(data), '')
  print
  
  print "getLinkCode"
  test(getLinkCode(data), 'LL12')
  print

#  this doesn't work since hits changes every time we test.
#  print "getLinkHits"
#  test(getLinkHits(data), 24)
#  print

  print "getLinkRating"
  test(getLinkRating(data), 8.64)
  print
  
  print "getLinkVotes"
  test(getLinkVotes(data), 1514)
  print
  
  print "getLinkRank"
  test(getLinkRank(data), 5503)
  print
  
  print "getLinkCategories"
  test(getLinkCategories(data), ['Humor', 'Pictures'])
  print

  print "getLinkDescription"
  test(getLinkDescription(data), 'I believe you have my stapler.')
  print

def getEnclosedString(text, startString='', endString=''):
  """
  Given some text and two strings, return the string that is encapsulated by the first sequence of these two strings in order.
  If either string is not found or text is empty, return the empty string.
  """
  if not len(text):
    return ""
  stringMatch = re.search(startString + r'(.+?)' + endString, text)
  if not stringMatch:
    return ""
  return stringMatch.groups()[0]

def getLinkTitle(text):
  """
  Given HTML of a link page, return link title or empty string if title not found.
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
  creatorList = getEnclosedString(text, r'\<b\>Added by\:\<\/b\> \<a href\=\"profile\.php\?user\=', r'\<\/a\>\<br \/\>').split('">')
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
  return int(getEnclosedString(text, '<b>Hits:</b> ', r'<br />'))

def getLinkRating(text):
  """
  Given HTML of a link page, returns the rating of this link.
  """
  return float(getEnclosedString(text, '<b>Rating:</b> ', r'/10')) 

def getLinkVotes(text):
  """
  Given HTML of a link page, returns the number of votes on this link.
  """
  return int(getEnclosedString(text, r'\/10 \(based on ', r' votes\)\<br \/\>'))

def getLinkRank(text):
  """
  Given HTML of a link page, returns this link's rank.
  """
  return int(getEnclosedString(text, r'<b>Rank:</b> ', r'<br/>')) 

def getLinkCategories(text):
  """
  Given HTML of a link page, returns list of link categories.
  """
  return getEnclosedString(text, '<b>Categories:</b> ', '<br />').split(', ')

def getLinkDescription(text):
  """
  Given HTML of a link page, returns the link description.
  """
  return getEnclosedString(text, '<b>Description:</b>\s+', '  <br /><br />')

def reportLink(opener, linkID, reason, comments):
  """
  Reports linkID for specified reason and appends comments.
  """
  if not opener or not int(linkID) or not int(reason) or not len(comments):
    return False
  params = urllib.urlencode(dict([('r', int(reason)), ('c', comments)]))
  report_link = opener.open('https://links.endoftheinter.net/linkreport.php?l='+str(int(linkID)), params)
  data = report_link.read()
  report_link.close()
  # LL doesn't provide any feedback upon reporting a link so we have to assume that all went well.
  return
  
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
  
def checkLinkNeedsReporting(text, tag_dict, site_dict):
  """
  Checks to see if a link needs to be reported.
  Checks several things:
  1.  If there are [TAGS] in the title, checks to ensure categories are properly set for those tags.
  2.  If there are links to sites specified by site_dict within the link description or actual link, 
      checks those to see if they're down and if this link is tagged with the 'Uploads' category.
  Returns False if all the checks pass (or the link is deleted), a list of reasons if not.
  """
  if checkLinkDeleted(text):
    return False
  
  reason_list = []
  
  # check to make sure that any [TAGS] in the title are properly-reflected in the categories.
  title = getLinkTitle(text)
  title_tags = re.findall(r'\[\S+?\]', title)
  categories = getLinkCategories(text)
  for tag in title_tags:
    if tag.upper() in tag_dict:
      for required_tag in tag_dict[tag.upper()]:
        if required_tag not in categories:
          reason_list.append((3, 'Needs category: ' + required_tag))
  
  # check link's link and description to see if there are links to popular upload sites.
  link = getLinkLink(text)
  link_match = re.search(r'(\w+\.com)', link)
  if link_match and link_match.groups()[0] in site_dict:
    base_url = link_match.groups()[0]
    link_external_site = urllib2.urlopen(link)
    site_text = link_external_site.read()
    link_external_site.close()
    if site_dict[base_url] in site_text:
      reason_list.append((2, 'Dead link.'))
  
  # if there are upload links in the link or description and this link isn't tagged as upload, flag this link to be reported.
  description = getLinkDescription(text)
  allText_matches = re.findall(r'(\w+\.com)', link + description)  
  if allText_matches:
    for base_url in allText_matches:
      if base_url in site_dict:
        if 'Uploads' not in categories:
          reason_list.append((3, 'Needs category: Uploads'))
  if reason_list:
    return reason_list
  else:
    return False

def main():
  
  args = sys.argv[1:]
  if not args or len(args) < 4:
    print "usage: [--no-report] username password startID endID";
    sys.exit(1)

  report_links = True
  if args[0] == "--no-report":
    report_links = False
    del args[0]
    
  llUsername = str(args[0])
  llPassword = str(args[1])
  startID = int(args[2])
  endID = int(args[3])

  opener = login(llUsername, llPassword)
  if not opener:
    print "Unable to log in with provided credentials."
    sys.exit(1)
  
#  runTests(opener)

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
    link_page = opener.open('https://links.endoftheinter.net/linkme.php?l='+str(linkID))
    text = link_page.read()
    link_page.close()
    if checkLinkExists(text):
      reasonList = checkLinkNeedsReporting(text, tag_dict, site_dict)
      if reasonList:
        reportComment = ""
        for tuple in reasonList:
          if not reportComment:
            reportComment = tuple[1]
          else:
            reportComment = reportComment + "\r\n" + tuple[1]
          lastReason = tuple[0]
        if report_links:
          data = reportLink(opener, linkID, lastReason, reportComment)
          print "Reported",
        print "linkID " + str(linkID) + " (type " + str(lastReason) + "): " + ", ".join(reportComment.split("\r\n"))
    # waiting sucks.
    if linkID % 100 == 0:
      print "Progress: " + str(round(100*(linkID - startID)/(endID - startID), 2)) + "% (" + str(linkID) + "/" + str(endID) + ")"
if __name__ == '__main__':
  main()
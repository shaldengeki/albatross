Albatross
=========

About
-----

Albatross (this iteration of it, anyways) is a Python library to programmatically access link and board data on endoftheinter.net. 

Albatross was originally designed as a link-reporting script, and retains much of that functionality. The checks it is capable of performing include:

1. Checking for the presence of popular [TAG]s in the link title, and ensures that link categories are set appropriately
2. Checking to see if links on popular upload sites are still active.

If one of the above checks fails, Albatross will automatically report the link to be handled by a link moderator. 

Note that, since links are currently down, none of the link-related functions will actually work! The boards-related functions will work perfectly fine in the meanwhile, though.

Albatross is licensed under the WTFPL. Do what you want with it!

Dependencies
------------

Albatross requires the following:

* [pytz](http://pytz.sourceforge.net)
* [pycurl](http://pycurl.sourceforge.net)
* [pyparallelcurl](https://github.com/petewarden/pyparallelcurl)

A copy of Pete Warden's fabulous pyparallelcurl is bundled, but you can feel free to replace it with a more up-to-date version if one exists.

Getting Started
---------------

To get started, simply install Albatross by doing `sudo python setup.py install`, and do:

    import albatross
    etiConn = albatross.Connection(username="LlamaGuy", password="hunter2")
    sampleTopics = etiConn.topics(allowedTags=["LUE"], forbiddenTags=["NWS"]).search(query="luelinks")
    print sampleTopics[0]

Alternatively, you can also provide a cookie string to Albatross in lieu of a username and password:

    etiConn = albatross.Connection(cookieString="your-cookie-string-here", cookieFile="your-cookie=file-here.txt")

By default, if you specify a username+password or cookieString+cookieFile pair upon construction, Albatross will attempt to re-authenticate with ETI if it detects that you have been logged out. If you've provided a username+password, it will attempt to log you back into ETI. If you've provided a cookiestring+file, it will reload the cookiestring from the provided file. You can disable this behavior when you call the constructor, like so:

    etiConn = albatross.Connection(username="LlamaGuy", password="hunter2", reauth=False)

This behavior is disabled by default if you specify a cookieString but no cookieFile, or if cookieFile does not exist on your system.

You can fetch topic posts like so:
    
    oneTopic = etiConn.topic(7823107)
    # alternatively:
    oneTopic = albatross.Topic(etiConn, 7823107)
    # or even:
    oneTopic = etiConn.topics(allowedTags=["Anime"]).search(query="Ritsu's", recurse=True)[0]
    print oneTopic.posts()[0]

And from there, post info like so:

    onePost = etiConn.post(104123023, oneTopic)
    # alternatively:
    onePost = albatross.Post(etiConn, 104123023, oneTopic)
    # or even:
    onePost = oneTopic.posts()[0]
    print onePost

You can also fetch user info:
    
    oneUser = etiConn.user(1)
    # alternatively:
    oneUser = albatross.User(etiConn, 1)
    # or maybe:
    someUsers = etiConn.users.search("guy", recurse=True)
    print oneUser

Finally, Albatross can also pull information about tags from ETI. For instance, you could do any of the following:
    
    activeTags = etiConn.tags(active=True)
    someTags = etiConn.tags(tags=["LUE", "Anonymous", "Anime"])
    someTagsTopics = someTags.topics().search()
    animeTag = etiConn.tag("Anime")
    animeTagTopics = animeTag.topics().search()
    print animeTag

For more info on available arguments and methods, please consult the help() documentation in your python console.

Tests
-----

If you're interested in running the tests that come with Albatross, you'll first have to create a textfile named credentials.txt in the base project directory, with your username and password on the first line, separated by commas. So, for example, I could put:

`LlamaGuy,hunter2`

and when I run Albatross's tests, it'll try to log into ETI as "LlamaGuy" with the password "hunter2". After that, running tests is as easy as doing `nosetests`!
Albatross
=========

About
-----

Albatross (this iteration of it, anyways) is a Python library to programmatically access link and board data on endoftheinter.net. 

Albatross was originally designed as a link-reporting script, and retains much of that functionality. The checks it is capable of performing include:

1. Checking for the presence of popular [TAG]s in the link title, and ensures that link categories are set appropriately
2. Checking to see if links on popular upload sites are still active.

If one of the above checks fails, Albatross will automatically report the link to be handled by a link moderator. Note that, since links are currently down, none of the link-related functions will actually work! The boards-related functions will work perfectly fine in the meanwhile, though.

Albatross is licensed under the WTFPL. Do what you want with it!

Getting Started
---------------

To get started, simply install Python, download albatross, and do:

    import albatross
    etiConn = albatross.Albatross(username, password)
    etiConn.searchTopics(allWords="luelinks")
    ...

Tests
-----

If you're interested in running the tests that come with Albatross, you'll first have to create a textfile named credentials.txt in the base project directory, with your username and password on the first line, separated by commas. So, for example, I could put:

`LlamaGuy,hunter2`

and when I run Albatross's tests, it'll try to log into ETI as "LlamaGuy" with the password "hunter2". After that, running tests is as easy as doing `nosetests`!
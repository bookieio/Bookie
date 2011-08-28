=========================
Browser Extensions
=========================
If you do not use Google Chrome, make sure to check out using the `Bookie
bookmarklet`_.

Google Chrome Extension
========================

Provides Bookie bookmarks into Google Chrome

Features
----------

- integrated popup dialog to save current site to your Bookie install.
- supports loading existing bookmark data if you're on a page already
  bookmarked
- Capable of sending current page's html content to Bookie for parsing the
  readable version of the page so it's immediately available. This slows down
  the plugin, so uncheck the *Cache Content* if you experience adverse
  performance
- Assists by providing recently used tags for completion


Installation
------------

- Chrome users can get it from the Gallery: http://goo.gl/NYinc
  *Hint* good reviews would be appreciated!
- To get the development version of the extension (to use with the develop
  branch) use the url: http://docs.bmark.us/bookie_chrome.crx
- Updates currently need to be done manually

Setting up
----------
In order to setup the extension you'll need to set a couple of options. To pull
up the options page right-click on the extension in the toolbar and select the
*Options* menu.

API Url
    set this to the installed url for your bookie instance. In dev mode
    it's `127.0.0.1:6543`. If you do not set the api url you should get
    an error about not being able to find a bookie instance at that url.

API Key
    You can get the API key for your user by logging into the website and going
    to the *Account* page. There you will find a link for "View API Key" that
    will show you your key. The default login for a fresh install is a
    admin:admin.

Username
    This is the username for your account. This is used to help construct the
    api urls. The default user account is *admin*.

Cache Content
    If you check this, then the html of the page is sent to the Bookie
    installation when you click the button to save a bookmark. This means that
    Bookie will have the parsed *readable* version of the content immediately.
    This might pass large bits of data over and slow things down a little bit.
    If you find it too slow, uncheck and run the server side script provided
    via cron to get the *readable* version of your bookmark content.


Firefox Extension
==================

Currently under stalled development. Check out the `feature branch`_ for keeping
tabs on how it's progressing. It's currently woefully out of date and not using
the latest API code.

Features
--------

- integrated popup dialog to save current site to your Bookie install.
- supports loading existing bookmark data if you're on a page already
  bookmarked

Installation
-------------
There's an initial shot at the plugin awaiting review at `addons.mozilla.org`_.


.. _feature branch: https://github.com/mitechie/Bookie/tree/feature/ff_ext
.. _addons.mozilla.org: https://addons.mozilla.org/en-US/firefox/addon/bookie-for-firefox/
.. _Bookie bookmarklet: user.html#bookmarklet

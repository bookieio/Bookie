=========================
Browser Extensions
=========================
If you do not use Google Chrome, make sure to check out using the `Bookie
bookmarklet`_.

Google Chrome Extension
========================

Provides Bookie bookmarks into Google Chrome

.. image:: http://files.bmark.us/bmark.us_chrome_ext.png
    :width: 400

Features
----------

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
  branch) use the url: http://files.bmark.us/chrome_ext.crx
- Updates currently need to be done manually

Setting up
----------
In order to setup the extension you'll need to set a couple of options. To pull
up the options page right-click on the extension in the tool bar and select the
*Options* menu.

API Url
    set this to the installed url for your bookie instance. In dev mode
    it's `http://127.0.0.1:6543/api/v1`. If you do not set the api url you should get
    an error about not being able to find a bookie instance at that url.

    By default the extension attempts to hook you up to the bmark.us instance.

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
    installation when you click the button to save a bookmark. This might pass
    large bits of data over and slow things down a little bit.  If you find it
    too slow, uncheck and run the server side script provided via cron to get
    the *readable* version of your bookmark content.


Firefox Extension
==================

The Firefox extension is starting over from scratch. You can track it at:

- https://github.com/bookieio/bookie-firefox


.. _Bookie bookmarklet: user.html#bookmarklet

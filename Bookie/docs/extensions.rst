=========================
Browser Extensions
=========================

Google Chrome Extension
========================

Provides Bookie bookmarks into Google Chrome

Features
----------

- integrated popup dialog to save current site to your Bookie install.
- supports loading existing bookmark data if you're on a page already
  bookmarked

Installation
------------

- Download the extension from the url http://bmark.us/bookie_chrome.crx
- Updates currently need to be done manually

Setting up
----------
In order to setup the extension you'll need ot set a couple of options. To pull
up the options page right-click on the extension in the toolbar and select the
*Options* menu.

API Url
    set this to the installed url for your bookie instance. In dev mode
    it's `127.0.0.1:6543`. If you do not set the api url you should get an error
    about not being able to find a bookie instance at that url.

API Key
    this is the same key you set in your installations *.ini* config
    file. You should set this to be your own unique string and make sure that
    your server install and extension match. If they don't, you'll be unable to
    store bookmarks to your Bookie server.

Cache Content
    If you check this, then the html of the page is sent to the Bookie
    installation when you click the button to save a bookmark. This means that
    Bookie will have the parsed *readable* version of the content immediately.
    This might pass large bits of data over and slow things down a little bit.
    If you find it too slow, uncheck and run the server side script provided
    via cron to get the *readable* version of your bookmark content.


Firefox Extension
==================

Currently under active development. Check out the `feature branch`_ for keeping
tabs on how it's progressing.

.. _feature branch: https://github.com/mitechie/Bookie/tree/feature/ff_ext

.. Bookie documentation master file, created by
   sphinx-quickstart on Fri Feb  4 23:04:10 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Bookie's documentation!
==================================
Bookie is my attempt to rid myself of Delicious, and be able host my bookmarks
which I hold dear myself.

Beyond that, there's some features I think that are long overdue.

.. image:: http://uploads.mitechie.com/bookie_ui_04_17_11.png
    :width: 400


Bookie Features
----------------
- Google Chrome extension
- Delicious API compatibility
- Fulltext index and search of your bookmark descriptions and tags
- (dev) Cached copy of bookmark's content into a searchable index
- Popularity tracking of your most commonly used (clicked) bookmarks
- Support for Sqlite, MySQL, and Postgres


Contents:
---------

.. toctree::
   :maxdepth: 1

   started
   database
   hosting
   user
   extensions
   events
   development

.. Indices and tables
.. ==================
.. 
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


Upcoming Bookie Events
=======================
Check out the events_ schedule page for some dates of sprints and hacking times
for Bookie.

Using Bookie
============
So far, there's no real web interface. Personally, I use a Chrome extension for
most of my bookmark use and I'm starting there first. I've forked an open
source Chrome bookmark you can use to work with Bookie.

https://github.com/mitechie/delicious-chrome-extension

.. _events: events.html

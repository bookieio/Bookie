Bookie Features
=======================

Open source!
-------------
We're big fans of Open Source development. Bookie is AGPL licensed and we
encourage you to fork it from Github and try it out. Have a pet feature you'd
love to work with? Then let us know. Jump into our IRC channel #bookie on
freenode to chat with the other developers.

Importing bookmarks
--------------------
At this time we support importing the Delicious and Google Bookmark exports.
They're just html files. The importer detects which format you're got and will
process them all in one swoop. It should run pretty quickly, though if you have
over 5,000 bookmarks you might notice it taking a little bit to get through
them.

When importing, make sure you enter the API key that is set in your
installation's *.ini* file. That's the security measure that prevents others
from importing into your Bookie installation. That key should be changed from
the default.

Google Chrome extension
-------------------------------------
Most of the details are available over in the extension_ docs. Make sure that
after you install it, that you go into the options to configure it to talk to
your specific Bookie installation.

Firefox Extension
------------------
In the works, see the extension_ docs.

Bookmarklet
-----------
You can use a bookmarklet to save bookmarks from any other browser, including
mobile browsers. Log into your account and you can get a copy/paste-able
bookmarklet from your account page.

Fulltext indexing and seach
----------------------------
When you load bookmarks into the system they are put into a fulltext index that
makes things very searchable. The description field, extended description, and
the tags are put into this index.

If you have enabled the *readable* parsed version of your bookmarks then these
are also available for search, however it's a separate checkbox as it might
make searches slightly slower.

These indexes are updated as you add and delete bookmarks and should make
finding things much easier thank just looking for tags.

*Readable* cached copy of page content
--------------------------------------
Bookie now supports storing a cleaned version of the content of the page you
just bookmarked. You can either enable it via the Chrome extension options or
you can run the server side script provided in
*scripts/readability/existing.py* to collect the page content. It's not
perfect, but in testing it provides a decent trimmed down version of the pages.
This content is then indexed and made searchable. In the future we hope to use
this to provide fast mobile viewing of your bookmarks and possibly even the
ability to build 'books' of content that can be packaged together and turned
into e-book material.

This is all very much inspired by Instapaper_ and Readability_.

If you find pages of content that don't work well please let us know and we can
see if the code used to do the parsing can be tweaked to do a better job with
your content.

Popularity Tracking
-------------------
Every time a bookmark url is clicked on it's tracked and counted. This allows
us to provide a view of your bookmarks by popularity. We're hoping this
provides a very useful interface when we start working on our mobile views. In
the future we might also be able to provide some analytics much like `bit.ly`_
does for shortened urls.

Multi database support
----------------------
Bookie currently supports Sqlite, MySQL, and Postgresql as a storage backend.
This includes all of the fulltext indexing and searching. Obviously, how each
database performs these is a little bit different so you might find better luck
with some backends over others.


Mobile Friendly
~~~~~~~~~~~~~~~~
We're working on making the website mobile friendly using responsive design
techniques.

.. _extension: extensions.html
.. _Instapaper: http://instapaper.com
.. _Readability: http://readability.com
.. _bit.ly: http://bit.ly

User Docs
=========


Importing
----------
Bookie currently supports the Delicious export, Google Bookmarks export,
Google Chrome bookmarks, and Firefox JSON backups.

- Delicious - You can export from Delicious by going to `Settings` and clicking the `Import / Upload Bookmarks` link under the `Bookmarks` section.
- Google Bookmarks - You can export your Google bookmarks by going to ???
- Google Chrome - You can export by going to `Bookmark manager`, `Organize`,
  and then `Export bookmarks to HTML file...`.
- Firefox - You can generate a backup by going to `Show all Bookmarks`, then
  `Import and Backup`, and selecting `Backup...`.

The importer might take a bit on large sets of bookmarks. Let us know if you
run into any issues so we can improve our import process.

Readable Parsing of your Bookmarks
-----------------------------------
One of Bookie's best features is that it will fetch the content of your
bookmarks and attempt to parse/fulltext index it. A bookmark import will cause
the system to go in and start fetching content for the new bookmarks. There's
also a background task that will (by default) attempt to find any bookmarks
missing content and fetch it on an hourly basis.

Example cron jobs
~~~~~~~~~~~~~~~~~

::

    # run readable parsing on new bookmarks each morning at 1am
    0 1 * * * /path/to/bookie/env/bin/python /path/to/Bookie/scripts/readability/existing.py --ini=myconfig.ini --new

    # retry error'd parsing at 1am on the 1st of each month
    0 1 1 * * /path/to/bookie/env/bin/python /path/to/Bookie/scripts/readability/existing.py --ini=myconfig.ini --retry-errors

Backup your Bookie bookmarks
-----------------------------
There's a quick/dirty `sample script`_ you can use to backup your bookmarks. It
just calls the `/export` url on your installation and creates a `.gz` backup
file.

This obviously doesn't store things like the fulltext indexes and such. So if
you are using the Readable versions you might want to keep a backup of your
database itself instead of just dumping your export file.

A sample of cron'ing this to run at 6am every day would be:

::

  0 6 * * * /usr/bin/python /path/to/Bookie/scripts/misc/backup.py

.. _sample script: https://github.com/bookieio/Bookie/blob/develop/scripts/misc/backup.py

Bookmarklet
-----------
To use the bookmarklet, log into your account page and drag the link at the
bottom to your bookmark bar. In the Android browser, you can long-press on the
link and bookmark it.

After that, you can bookmark any page you're currently viewing by clicking on
the bookmark in your browser. It will load the current url and page title into
an add form on the website.

Once you stored the bookmark with tags and description, you'll be redirected
back to the page you were originally viewing.

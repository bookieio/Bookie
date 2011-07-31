User Docs
=========


Importing
----------
Bookie currently supports the Delicious export and the Google Bookmarks export
formats.

- Delicious - You can export from Delicious by going to `Settings` and clicking the `Import / Upload Bookmarks` link under the `Bookmarks` section.
- Google Bookmarks - You can export your Google bookmarks by going to ???

The importer might take a bit on large sets of bookmarks. Let us know if you
run into any issues so we can improve our import process.

Readable Parsing of your Bookmarks
-----------------------------------
In order to get the parsed readable version of your bookmark content you can
use the script *scripts/readability/existing.py*

Parameters
~~~~~~~~~~

--ini
    (Required) what is the *.ini* file we're using to do things like figure out
    the db connection string?

--new
    Only go through and fetch/parse html content for bookmarks that have not
    been processed before. You might use this in a daily cron script to update
    readable content for new bookmarks.

--retry-errors
    Go through and retry any bookmarks that were not a successful status code
    of 200 during a previous run. You might want to run this once a month to
    see if any previous 404'd bookmarks are available now, etc.

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

.. _Chrome Plugin: extensions.html
.. _sample script: https://github.com/mitechie/Bookie/blob/develop/scripts/misc/backup.py

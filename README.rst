Bookie
========
:Main Site: https://bmark.us
:Docs: http://docs.bmark.us
:Mailing List: https://groups.google.com/forum/?hl=en#!forum/bookie_bookmarks
:Twitter: http://twitter.com/BookieBmarks
:Build Server: http://build.bmark.us

Bookie will one day be a self-hosted bookmark web-service similar to
Delicious.

Check out the main site for documentation on features, how to get started
installing, and where we're heading from here.

You can check out the Trello board to see what stuff is in the works atm and
what the status of your favorite pet feature is:

https://trello.com/board/bookie/4f18c1ac96c79ec27105f228

Quick Start
-----------
If you're on Ubuntu, you should be able to get started with:

::

    $ git clone git://github.com/bookieio/Bookie.git
    $ cd Bookie && make sysdeps && make install && make run
    $ google-chrome (or other browser) http://127.0.0.1:6543

Developing
-----------
If you wish to hack on Bookie with the rest of us please check out the
`HACKING.rst` doc in this tree.

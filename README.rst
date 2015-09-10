Bookie
========
:Main Site: https://bmark.us
:Public Bookie Instances: https://github.com/bookieio/Bookie/wiki/Bookie-instances
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

If you're on anything else, give our Vagrant image a try. If you don't have it already, you'll need to download and install Vagrant:

http://www.vagrantup.com/downloads.html

After that, you should be able to get started with:

::

    $ git clone git://github.com/bookieio/Bookie.git
    $ cd Bookie
    $ vagrant up
    $ vagrant ssh
    % cd /vagrant
    % make run
    $ google-chrome (or other browser) http://127.0.0.1:4567

Note: If you run into problems during the `make sysdeps && make install` process, run `make clean_all` to reset the environment prior to re-running `make sysdeps && make install`.

If you're unable to complete the install process and need additional help please feel free to contact us in the #bookie IRC channel on Freenode, or the mailing lists.

Developing
-----------
If you wish to hack on Bookie with the rest of us please check out the
`HACKING.rst` doc in this tree.

Related
-------

The `Willie <http://willie.dftba.net/>`_ bot has a `contrib module to post bookmarks from IRC <https://github.com/anarcat/willie-extras/blob/bookie/bookie.py>`_. It is `not yet part of the extras repository <https://github.com/embolalia/willie-extras/pull/55>`_.

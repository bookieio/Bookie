====================
Contribute To Bookie
====================

To start contributing to Bookie, here is some info you might want to check out.

Quick Start
===========
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

Issues
======
The current issues related to Bookie can be seen at https://github.com/bookieio/Bookie/issues

Community
=========
Our users and developers use Mailing lists and Internet Relay Chat (IRC).

:Mailing List: https://groups.google.com/forum/?hl=en#!forum/bookie_bookmarks
:IRC: http://webchat.freenode.net/?channels=bookie

Hacking
=======

.. toctree::
   :maxdepth: 2
   
   hacking

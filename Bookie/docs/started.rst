Getting Started
===============

Bookie's git repository is managed using a tool/process called `git flow`_. It
basically sets standards for how the git repository is set up. You'll find the
most up to date *working* code in the develop branch. Individual features that
are being worked on are in branches prefixed by `feature/`. As these features
get to a workable state they might get merged into the `develop` branch.

The `master` branch is only for releases and we're a long away from that. So
when you check out Bookie, make sure to start out using the `develop` branch.

Some basic docs on getting started with the project. Before you ask, yes this
will get much easier as the project moves forward. It's in development mode
still.


Ubuntu Linux
------------
If you're running Ubuntu, here's some actual commands to get you started.


::

  $ wget http://bmark.us/bootstrap.py
  $ python bootstrap.py bookie
  $ source bookie/bin/activate
  $ cd bookie/bookie/Bookie/

  # $myname is a name you're giving your installation. Just one word will do
  $ fab new_install:$myname

  # this will create a config file for you called $myname.ini
  # feel free to edit this config for your needs and then
  $ fab $myname db_new_install

  # startup the development web server
  $ paster serve --reload $myname.ini

You should now be able to pull up:

http://127.0.0.1:6543


To Do
~~~~~~
- Update the bootstrap.py to use a tarball source to avoid git requirement
- Link to the hosting docs about setting up bookie to run for good


Where to go from here
---------------------
Well, you might want to import a backup of your delicious bookmarks. You can do
that with

::

  $ python bookie/scripts/import_delicious.py delicious_file.htm

You can view your recent bookmarks at:

http://127.0.0.1:6543/recent


You can also start using the `Google Chome extension`_ in development to save and
edit bookmarks you have in Bookie. It will only work based on the current page,
a full UI for managing your bookmarks is in the works.


.. _`git flow`: https://github.com/nvie/gitflow
.. _`Google Chome extension`: https://github.com/mitechie/delicious-chrome-extension

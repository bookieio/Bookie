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

  $ sudo apt-get install python-virtualenv
  $ virtualenv --no-site-packages bookie_ve
  $ cd bookie_ve
  $ source bin/activate
  $ git clone git://github.com/mitechie/Bookie.git
  $ cd Bookie/Bookie/
  $ git checkout develop
  $ pip install -r requirements.txt

  # and now we wait while pypi does it's thing and installs dependencies

  $ python setup.py develop

  $ fab dev db_init
  $ fab dev db_upgrade
  # for some reason we have to resource the virtualenv
  $ source ../../bin/activate
  $ paster serve --reload development.ini

You should not be able to pull up:

http://127.0.0.1:6543

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

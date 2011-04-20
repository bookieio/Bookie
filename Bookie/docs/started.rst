Getting Started
===============

Some basic docs on getting started with the project. Before you ask, yes this
will get much easier as the project moves forward. It's in development mode
still.

Ubuntu Linux
------------
If you're running Ubuntu, here's some actual commands to get you started.


Note: right we we support all three databases and the database bindings need to
be built into the virtualenv. To do this you need some packages:

- libmysqlclient-dev
- postgresql-server-dev-9.0 (or 8.4 if that's your current version)
- build-essential
- python-dev

We're hoping to `clean this up some`_ some going forward.

We also need these packages for the content parsing library used, decruft:

- ibxslt1-dev
- libxml2-dev

For the copy/paste crowd:

::

    sudo apt-get install libmysqlclient-dev postgresql-server-dev-8.4 build-essential python-dev ibxslt1-dev libxml2-dev

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


Where to go from here
---------------------

Getting your bookmarks into Bookie
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Well, you might want to import a backup of your delicious bookmarks. You can do
that by vising the *Import* link in the footer of your site installation

You can view your recent bookmarks at: http://127.0.0.1:6543/recent

You probably also want to install a `browser extension`_ to be able to store
new bookmarks going forward. Once you install the extension, you'll need to set
the options for it to work. See the `browser extension`_ docs for those
settings.


Hosting Bookie
~~~~~~~~~~~~~~
You can setup Bookie to run in a variety of ways. Make sure to check out some
samples in the `hosting docs`_


To Do
~~~~~~
- Update the bootstrap.py to use a tarball source to avoid git requirement

.. _`git flow`: https://github.com/nvie/gitflow
.. _`Google Chome extension`: http://bmark.us/bookie_chrome.crx
.. _`hosting docs`: hosting.html
.. _`clean this up some`: https://github.com/mitechie/Bookie/issues/37

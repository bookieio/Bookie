Getting Started
===============

Some basic docs on getting started with the project. Before you ask, yes this
will get much easier as the project moves forward. It's in development mode
still.

Ubuntu Linux 10.10
------------------

OS Packages
~~~~~~~~~~~~
There are some required packages that need to be installed so you can build bookie. These are:

- build-essential
- python-dev
- libxslt1-dev
- libxml2-dev
- git

Note: right we we support three databases - mysql, postgres, and sqlite - and the database bindings need to be built into the virtualenv. We're hoping to `clean this up some`_ some going forward.

MySQL & Postgresql Users
~~~~~~~~~~~~~~~~~~~~~~~~
If you're using Postgres or MySQL as your database for Bookie you'll also want
to grab the dev package for your db so that the Python drivers for them can
compile.

- libmysqlclient-dev
- postgresql-server-dev-8.4

Ubuntu 10.10 (Maverick Commands)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you're running Ubuntu 10.10 (Maverick), here's some actual commands to get you started.

::

  # install the required packages to build bookie
  # (just needs to be run once)
  $ sudo apt-get install build-essential libxslt1-dev libxml2-dev python-dev git

  # Mysql & Postgresql users
  $ sudo apt-get install libmysqlclient-dev
  # - OR -
  $ sudo apt-get install postgresql-server-dev-8.4

  # go to where you want the bookie source to live and install dependencies
  $ cd to/some/directory/
  $ wget http://bmark.us/bootstrap.py
  $ python bootstrap.py bookie

  # activate the python virtualenvironment
  $ source bookie/bin/activate

  $ cd bookie/bookie/

  # Create a new fabric configuration file.
  # $myname is a name you're giving your installation. Just one word will do
  # This will create a config file for you called $myname.ini
  # Feel free to edit this config for your needs (port, apikey, etc).
  $ fab new_install:$myname
  $ fab $myname db_new_install

  # Startup the development web server with your configuration.
  $ paster serve --reload $myname.ini

You should now be able to pull up:

http://127.0.0.1:6543


Where to go from here
---------------------

Getting your bookmarks into Bookie
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Well, you might want to import a backup of your delicious bookmarks. You can do
that by vising the *Import* link in the footer of your site installation. Make
sure you know the API key that you've set in your bookie install's *.ini*
configuration file.

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

.. _`browser extension`: extensions.html
.. _`hosting docs`: hosting.html
.. _`clean this up some`: https://github.com/mitechie/Bookie/issues/37

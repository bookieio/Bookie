=================
Installing Bookie
=================

There's two ways to do it. If you're a developer and want to use git,
virtualenv, and fabric to get started, then check out `Installing the long
way`_.

Otherwise, use the shorter way that gets bootstrapped for you below.

The easy way
============

Tested on Ubuntu Linux 10.10

OS Packages
~~~~~~~~~~~~
There are some required packages that need to be installed so you can build bookie. These are:

- build-essential
- python-dev
- libxslt1-dev
- libxml2-dev
- git

::

    # install the required packages to build bookie
    $ sudo apt-get install build-essential libxslt1-dev libxml2-dev python-dev git


Note: right we we support three databases - mysql, postgres, and sqlite - and the database bindings need to be built into the virtualenv.


MySQL & Postgresql Users
~~~~~~~~~~~~~~~~~~~~~~~~
If you're using Postgres or MySQL as your database for Bookie you'll also want
to grab the dev package for your db so that the Python drivers for them can
compile.

- libmysqlclient-dev
- postgresql-server-dev-8.4

::

    $ sudo apt-get install postgresql-server-dev-8.4
    - OR -
    $ sudo apt-get install libmysqlclient-dev

Ubuntu 10.10 (Maverick Commands)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you're running Ubuntu 10.10 (Maverick), here's some actual commands to get you started.

Go to where you want the bookie source to live and install dependencies

::

    $ cd to/some/directory/
    $ wget http://files.bmark.us/bootstrap.py
    $ python bootstrap.py bookie


Activate the virtual environment

::

    $ source bookie/bin/activate
    $ cd bookie/bookie/

Create a new fabric configuration file for your environment. [myname] is the
name of the environment. For instance, you might call your environment *dev* or
*rick*. This would create a config file for your name named *[myname].ini*.

::

    $ fab new_install:[myname]
    $ fab [myname] db_new_install

Then startup your development web server to test the website.

::

    $ paster serve --reload [myname].ini

You should now be able to pull up: http://127.0.0.1:6543


Where to go from here
~~~~~~~~~~~~~~~~~~~~~~~

Getting your bookmarks into Bookie
-----------------------------------
Well, you might want to import a backup of your delicious bookmarks. You can do
that by vising the *Import* link in the footer of your site installation. Make
sure you know the API key that you've set in your bookie install's *.ini*
configuration file.

You can view your recent bookmarks at: http://127.0.0.1:6543/recent

Installing Extension
---------------------
You probably also want to install a `browser extension`_ to be able to store
new bookmarks going forward. Once you install the extension, you'll need to set
the options for it to work. See the `browser extension`_ docs for those
settings.

Hosting Bookie
---------------
You can setup Bookie to run in a variety of ways. Make sure to check out some
samples in the `hosting docs`_



Installing the long way
===============================

If you don't use the `bootstrap.py` to install Bookie, you can perform its
steps manually. The idea is to setup a virtualenv_ to install Bookie into. The
list of app packages required for development work are in the
`requirements.txt` file with hard locked versions that help make sure things
work.

These instructions assume you will be installing Bookie on an Ubuntu machine.
You may need to translate these steps for your particular environment. (Better
yet, please supply us with the steps you used to get your environment working.)

::

  # install the required packages to build bookie
  # (just needs to be run once)
  $ sudo apt-get install build-essential libxslt1-dev libxml2-dev python-dev git python-virtualenv

  # Mysql & Postgresql users
  $ sudo apt-get install libmysqlclient-dev
  # - OR -
  $ sudo apt-get install postgresql-server-dev-8.4

  # go to where you want the bookie source to live and install dependencies
  $ cd to/some/directory/
  $ virtualenv --no-site-packages .

  # activate the python virtualenvironment
  $ source bookie/bin/activate

  # get the bookie source
  $ git clone git://github.com/mitechie/Bookie.git bookie
  $ cd bookie

  # install deps
  $ pip install -r requirements.txt
  $ python setup.py develop

  # Create a new fabric configuration file.
  # [myname] is a name you're giving your installation. Just one word will do
  # This will create a config file for you called [myname].ini
  # Feel free to edit this config for your needs (port, apikey, etc).
  $ fab new_install:[myname] (Ignore the error that recommends that you re-run this command)
  $ fab [myname] db_new_install

  # Startup the development web server with your configuration.
  $ paster serve --reload [myname].ini

You should now be able to pull up: http://127.0.0.1:6543

.. _virtualenv: http://pypi.python.org/pypi/virtualenv


To Do
=====
- Update the bootstrap.py to use a tarball source to avoid git requirement

.. _`browser extension`: extensions.html
.. _`hosting docs`: hosting.html

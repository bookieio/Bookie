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

We're hoping to `clean this up some`_ some going forward.

We also need these packages for the content parsing library used, decruft:

- ibxslt1-dev
- libxml2-dev

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

You can also start using the `Google Chome extension`_ to save and edit
bookmarks you have in Bookie. It will only work based on the current page, a
full UI for managing your bookmarks is in the works.

Once you install the extension, you'll need to set the options for it to work.

API Url
    set this to the installed url for your bookie instance. In dev mode
    it's `127.0.0.1:6543/delapi/`. Make sure to include the */delapi/* in the url
    for the extension to work. If you do not set the api you should get an error
    on the extension icon badge *!URL*


API Key
    this is the same key you set in your installations *.ini* config
    file. You should set this to be your own unique string and make sure that
    your server install and extension match. If they don't, you'll be unable to
    store bookmarks to your Bookie server.

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

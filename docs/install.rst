===============================
Installing the long way
===============================

If you don't use the `bootstrap.py` to install Bookie, you can perform its
steps manually. The idea is to setup a virtualenv_ to install Bookie into. The
list of app packages required for development work are in the
`requirements.txt` file with hard locked versions that help make sure things
work.

These instructions assume you will be installing Bookie on an Ubuntu machine. You may need to translate these steps for your particular environment. (Better yet, please supply us with the steps you used to get your environment working.)

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
  $ git clone git://github.com/mitechie/Bookie.git
  $ cd Bookie

  # install deps
  $ pip install -r requirements.txt
  $ python setup.py develop

  # Create a new fabric configuration file.
  # $myname is a name you're giving your installation. Just one word will do
  # This will create a config file for you called $myname.ini
  # Feel free to edit this config for your needs (port, apikey, etc).
  $ fab new_install:$myname (Ignore the error that recommends that you re-run this command)
  $ fab $myname db_new_install

  # Startup the development web server with your configuration.
  $ paster serve --reload $myname.ini

You should now be able to pull up:

http://127.0.0.1:6543

.. _virtualenv:

.. Bookie documentation master file, created by
   sphinx-quickstart on Tue Aug 24 08:49:21 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Bookie's documentation!
==================================
Bookie is an online bookmark management application.

Source
    https://github.com/mitechie/bookie

Docs
    `http://bookie.mitechie.com`__

.. _docs: http://bookie.mitechie.com

__ docs_

Contents:
----------

.. toctree::
   :maxdepth: 1

   design_ideas
   known_issues
   fabric
   api/index


Getting started
---------------
Bookie is designed to live in a `virtualenv`_. Create an empty virtualenv and then
check out the repository into a ``src`` directory.

.. _virtualenv: http://pypi.python.org/pypi/virtualenv

::

    $ source bin/activate
    $ mkdir src
    $ git clone git@github.com:mitechie/bookie.git src/bookie_app
    $ pip install -E . fabric
    $ cd src/bookie_app
    $ fab pip_update
    $ python setup.py develop


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


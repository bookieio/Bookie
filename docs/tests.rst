Bookie Tests
============

Running Tests
--------------
Running the test suite for Bookie is very simple:

::

  $ cd Bookie/Bookie/
  $ fab test

Test Types
-----------

Unit Tests
~~~~~~~~~~
Unit tests are small tests that should test small bits of code. These should be
setup in the same directory that the file you're testing is setup. So if you're
working on a file in `lib/feature.py` you'd have a matching file
`test_feature.py`. This file should be runnable via the test runner by itself.

Functional Tests
~~~~~~~~~~~~~~~~~
Functional tests are larger scope tests that make sure the application is
responding correctly as a whole. These are run through the fabric command `fab
test`. It will run all tests defined in the tests directory.

*Note:* All unit tests should be added to the `tests/__init__.py` so that they
get run during the large test run. This way the ci server will just need to run
the one test pass and all tests will run during each build.

Testing Docs
~~~~~~~~~~~~~
A bit confusing. There's lots of docs, but none of them seem to agree on how to
bootstrap the environment properly.

* http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html
* https://bitbucket.org/sluggo/pyramid_sqla/src/d826ad458869/demos/SimpleDemo/simpledemo/tests.py
* http://docs.pylonsproject.org/projects/pyramid/1.0/tutorials/wiki2/definingviews.html#adding-tests


Testing Javascript
~~~~~~~~~~~~~~~~~~
There are *fabfile* commands for testing the Javascript we have so far. It's
located in the *extensions* directory since that's where most of the JS lives.
We symlink it to the main site and such.

::

    $ fab jstest
    $ fab jsview

Will run the tests. This runs them through phantom.js_. It's using Qunit_ to
run the tests. There are a set of live api tests in there that will his
http://dev.bmark.us to verify that the api is in fact working as expected. This
loads up our JS implementation of the api *bookie.api.js*.


.. _phantom.js: http://www.phantomjs.org/
.. _Qunit: http://docs.jquery.com/Qunit

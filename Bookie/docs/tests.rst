Bookie Tests
============


Delicious Tests
---------------
We want to make sure our api is compatible with Delicious. We should make sure
existing libraries can save/query just as if we were delicious.com

Tests are pulled using the library: http://code.google.com/p/pydelicious/

Functional Testing
------------------
http://docs.pylonsproject.org/projects/pyramid/dev/narr/testing.html

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

*Note:* that all unit tests should be added to the `tests/__init__.py` so that
they get run during the large test run. Once I get a ci server up, it'll just
run the one test pass and all tests should get tested/passed during each build.

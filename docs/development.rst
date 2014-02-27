===============================
Development
===============================

Bookie is a Python web application written using the Pyramid_ web framework.

Bookie's git repository is managed using a tool/process called `git flow`_. It
basically sets standards for how the git repository is set up. You'll find the
most up to date *working* code in the develop branch. Individual features that
are being worked on are in branches prefixed by `feature/`. As these features
get to a workable state they might get merged into the `develop` branch.

The `master` branch is only for releases and we're a long away from that. So
when you check out Bookie, make sure to start out using the `develop` branch.

If you want to help out with the hacking of Bookie, here's some info you might
want to check out:


Contents:
---------

.. toctree::
   :maxdepth: 1

   changes
   makefile
   tests
   api
   todo
   events

.. _Pyramid: http://docs.pylonsproject.org/en/latest/docs/pyramid.html
.. _`git flow`: https://github.com/nvie/gitflow

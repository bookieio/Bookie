==========
Change Log
==========

Ok, so I'm going to try to summarize changes here, but for full changes see the
commit log. Commit often and all that.

What's new in 0.4
==================
0.4 was all about the port from jQuery to YUI for the Javascript side of
things. This meant that the UI got a big facelift, we've moved to the YUI MVC
framework, and the extensions needed to be updated to use the new library of
code.

We also spent time getting most of the fabric tasks moved over to the Makefile
to help aid in running and managing the installation.

What's new in 0.3
==================
The main goals of 0.3 were to add a full JSON API and to add authentication so
that a single Bookie install could support multiple users. This involved a ton
of changed code and so a lot more has changed in the process.

- new json api, see the `api docs`_ for details on usage. See *bookie.api.js*
  for an implementation of most of it.
- auth works. There's a whole forgotten password process and a fabric function
  for adding new users. We'll work on a real signup/register front end at some
  point before things get all public.
- Updated the CSS to be generated using Sass_
- update to the chrome extension, supporting recent tags used, better
  completion, better error handling, and sync of bookmarks you've bookmarked
  before
- Lots of documentation updates. Updated install docs, full api docs, cleaned
  up some of the other docs in the process.
- update to pyramid 1.1
- added the start of the tag commands framework so that we can have *!sometag*
  perform a specific command on the server side when storing a bookmark



.. _sass: http://sass-lang.com/
.. _api docs: http://docs.bmark.us/api.html

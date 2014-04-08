=============================
Hacking Events
=============================

Sprint: Saturday Aug 31st
----------------------------

:Location: `@mitechie`_'s house. Ping him for details.
:Time: 11am

Tasks
~~~~~
The main task is to work on test coverage of Bookie. We'll be using
`coverage.py`_ to find areas missing tests and work on getting better coverage
for them.

A couple of people have expressed interest in working on `breadability`_ and
some sites it's not processing that well.

Lunch will be provided and if you're interesting in working on something else
please let me know. The day will end when people get tired of sprinting.


Sprint: July 27th and 28th
----------------------------

:Location: PyOhio see @mitechie for where on Friday and Saturday info is on the
:Site: http://pyohio.org/Sprints/
:Time: Refer to the PyOhio site for details.

Tasks
~~~~~
We'll be working on any of the Bookie part of apps. This includes
`breadability`_, `bookie_parser`_, `bookie_firefox`_, `bookie_android`_. So if you want to
hack on a Pyramid app, celery processing, parsing algorigthms, Tornado apps on
Heroku, or CoffeeScript we've got something you can work on.

Specific task ideas include:

- Introduction to bookie and working on small bugs from the issue list.
- Update Bookie's readable parsing to be Celery driven to the bookie_parser
  service api.
- Work on Bookie's mobile/responsive UI and a possible two pane reader layout.
- Update Bookie's celery backend and port more current cron scripts over to Celery
  tasks.
- Working on fixing the breadability parser for web sites it's failing to
  parse
- Update breadability to provide metadata on processing including potential
  backup nodes of content, timing information, etc.
- Update the bookie_parser application to have some better webui.
- Add full metadata fetching of content from bookie_parser.
- Work on turning Bookie's Firefox extension into a CoffeeScript application
  that works against the bookie API.


Sprint: PyCon! March 12th-15th
--------------------------------
:Location: PyCon Sprints!
:Time: All the time!

Tasks
~~~~~~
- Get 0.4 out the door, this means FF extension completed and do a release
- Start 0.5 release, possible items include:

    - Signup system with throttled registrations/waiting list + api/ui for it
    - In place editing
    - Easy reader UI for !toread bmarks
    - Look at adding smarter tag suggestions (js page parser + smarter server
      side)
    - Celery/out of process worker system for things
    - Rework the url parsing worker for the celery backend, requests, async
    - get yeti and browser functional tests running SST?
    - better mobile/responsive UI bits
    - Stats stats and more stats API/UI

Sprint: Feb 25th
-----------------
Location: My Place
Time: 10am-4pm

Tasks
~~~~~~
The main task is to work on a full Firefox extension based off the add-on SDK.
Current base is located:

- https://github.com/bookieio/bookie-firefox

Misc Tasks
~~~~~~~~~~
A lot's changed. We could use help with:

- Installation testing
- Updating the current failing unit tests broken by recent code changes
- Documentation updates
- Working on UI updates/css tweaks for the mobile/media query drive UI
- Adding JS tests for the new JS driven UI
- Implementing DELETE in the chrome extension
- anything else we can think up.


Sprint: July 29th and 30th
----------------------------

Location: PyOhio see @mitechie for where on Friday and Saturday info is on the
site: http://pyohio.org/Sprints/
Time: Friday will be in the evening and Saturday with the PyOhio peeps after
the conference

Tasks
~~~~~
- Update documentation for the full set of api commands (see routes.py and
  views/api.py)
- Update documentation with screenshots from more recent builds (including the
  extension, website, and such)
- Generally documentation updates/clarifications regarding feature sets and such
  added in 0.3. A full changelog based on commits from 0.2 to current
- Testing of the mobile view against android and iOS for issues with jQuery
  mobile updates
- Adding a "save bookmark" form view. Basically implementing the extension
  popup in the website.
- Adding a bookmarklet that uses the above form to save the current page via
  the bookmarklet so it works from mobile and non-chrome browsers
- Keep working on updated FF extension using the extension builder code in the
  FF branch under the firefox_ext_addon_sdk

Current 0.4 Tasks
`````````````````
- Update to pyramid 1.1
- add some css styling to the readable view for website + mobile view
- Add a !private tag command which sets private on the bookmark of the user
- Start celery task runner for running stats against individual bookmarks daily

Sprint: April 22nd 2011:
--------------------------

The plan
~~~~~~~~
We're going to have the first ever Bookie sprint on Friday the 22nd of April.
Some potential goals:

- Work on getting the FF plugin working
- Some UI design/ideas pitching/feedback
- Test out the new readable parsing on everyone's batches of bookmarks
- Work on some docs updates and try to knock out a few items from the issue
  list for 0.2 : https://github.com/bookieio/Bookie/issues?milestone=5&state=open

Schedule
~~~~~~~~
The doors open up at 11am and we'll have some lunch delivered around 12:30pm.
I'll chase everyone away somewhere around 4pm.


.. _breadability: https://github.com/bookieio/breadability
.. _bookie_parser: https://github.com/bookieio/bookie_parser
.. _bookie_firefox: https://github.com/bookieio/bookie-firefox
.. _bookie_android: https://github.com/bookieio/Bookie-Android
.. _coverage.py: http://nedbatchelder.com/code/coverage/
.. _@mitechie: https://twitter.com/mitechie

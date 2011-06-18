Readable Parsing
=================

The system will handle fetching the html content of pages and running that
through a readable filter. We're using the library Decruft.  Once parsed, we
store that content so you can search and pull that up later.

There are currently three ways to load that content into the system.

1. Google Chrome Extension
---------------------------
The chrome extension supports a checkbox in the options that sends the current
page's html along for the ride when you add or edit a bookmark. In this way the
content is ready for your use right away.

2. existing.py
---------------
`existing.py` is a sample script writting in python that fetches a list of
unparsed urls from your install and starts fetching/parsing them. It was the
first script made to do it and is synchronous. On large bookmark lists it
might take a while for this to run. It was averaging some 1 bookmark/s on my
test system.

3. Let's complicate it, node.js, beanstalkd, and the api
---------------------------------------------------------
In order to have a method that was more performant, there's a system you can
use to really crank through these. There's much more setup involved.

The system is built around a new pair of API calls that will return a list of
unparsed urls and that you can feed information about an attempt to load html
content. The `readable_producer.js` is a node.js script that will run through
the list of bookmarks to parse and async fetch their content. If the content is
there and ok, it'll place that into a beanstalkd queue. If not, it'll create a
list of what went wrong and stick that in the queue.

The `readable_consumer.py` is meant to be run several times to read items off
the queue and to make API calls to the bookie installation. It will send the
content to bookie to run through the parser and store in the database. Since
this is sync code, we want to run multiple versions of this. In testing, I was
able to run 4 against a sqlite database, and 8 against postgresql backed bookie
install.

This method of running could be scaled well over 5 urls parsed and put into the
bookie database per second.

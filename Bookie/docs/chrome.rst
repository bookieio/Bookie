Google Chrome Extension
========================

Provides Bookie bookmarks into Google Chrome

Features
----------

- integrated popup dialog to save current site to your Bookie install.
- supports loading existing bookmark data if you're on a page already
  bookmarked

Installation
------------
The `manifest.json` file has to be updated for the url you're hosting your
Bookie instance on. In the future, we should try to provide a bundling service
where you enter that url, and we write out the manifest and provide a
downloadable package ready to go.

For now you must manually load the directory into your extensions as an
unpackaged extension. You have to manually make sure your Bookie url is in the
list of permitted urls so that it can make cross domain ajax requests to store
and retrieve data.

Mitechie Fork
--------------
I've forked this to be able to customize the delicious api url to work with my
own bookmark app. You can basically change the url to whatever in the
delicious.js file and add the directory into Chrome as an unpacked extension.
Will try to work on this to add some ui for adjusting the ui from the options
along with some tweaks to help provide some search/etc feedback of existing
bookmarks.

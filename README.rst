Bookie
========
:Docs: http://bmark.us

Bookie will one day be a self-hosted bookmark web-service similar to Delicious
with associated integration with command-line clients and browswer plugins.

Using Bookie with Google Chrome
-------------------------------
For now, there's a alpha Google Chrome plugin that's forked from an `open source
extension`_.

What's going on?
================
I started this a few times and have pylons code in the pylons dir that never
got far. It's been moved off to the side, all progress and new code is moving
forward in the Bookie directory which is a Pyramid app going forward.
=======
.. _open source extension: https://github.com/wireframe/delicious-chrome-extension

It supports saving, editing, and removing bookmarks to an instance. In order to
use it, you must manually load the extension into Chrome and set your bookie
install url instance as a permitted host in the `manifest.json` file.

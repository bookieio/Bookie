Fabric controls
===============

We want to try to abstract and wrap functions needed into fabric commands. This
should help us keep things close to automated, in one place to find, and
hopefully usable for remote/installed instances down the road.

Directory fabfile
-----------------
Commands are put into the module/directory named `fabfile`. In there will be a
list of files, grouping controls and commands together for use. For instance
all of the database migration related commands should be in the `migrate.py`
file.

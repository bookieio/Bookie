=============
Known Issues
=============

SqlAlchemy Migrate
-------------------
We're working from SA .0.6.0 and SA Migrate has failing unit tests and isn't
released with full support yet. 

Might run into bugs using it. 


Migration for Triggers
-----------------------
Currently we're only doing the triggers in Sqlite syntax. Eventually we'll need
this to work with the final db chosen, but also want the Sqlite to work for unit
tests

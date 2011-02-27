Bookie Database Notes
=====================

The goal is for this to be self hostable. Ideally, Bookie will support MySQL,
Postgres, and Sqlite. Initially, we will work on a great working Postgres, but 
we can see people wanting little sites running locally just for managing 
bookmarks.

Migrations
----------
All database changes must be placed into a migration. The install process will
run through those. We're using SqlAlchemy and will be using
SqlAlchemy-Migrations to get it going.

Running Migrations
~~~~~~~~~~~~~~~~~~
Handling iterations with the migration layer should take place from within the
Fabric commands provided.

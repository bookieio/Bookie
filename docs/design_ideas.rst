===================
Bookie Design Ideas
===================

Datastore
=========
Notes on data storage/layout

Tables
-------

users
~~~~~

bookmarks
~~~~~~~~~
- id
- hash (hash)
- url

tags
~~~~
- id
- name
- count

users_tags
~~~~~~~~~~
- user_id
- tag_id
- tag_count

bookmarks_tags
~~~~~~~~~~~~~~
- bookmark_id
- tag_id

users_bookmarks
~~~~~~~~~~~~~~~
user_id
bookmark_id
bookmark_description
bookmark_extended
bookmark_date
bookmark_shared

bookmarks_meta
~~~~~~~~~~~~~~~
- bookmark_id
- frequent tags
- suggested tags
- date_pulled


Auth
====
So long term the way to go with this is to figure out OAuth. This will help with
keeping other tools working well. 

API
====
Notes on API available/delicious

Admin only calls
================
These are calls meant to help the admin with the system. Their documented for
the project's need.


/a/accounts/invites
-------------------

Usage
'''''
*GET* `/api/v1/a/accounts/invites`

Return a list of the users and the number of invites they have.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/a/accounts/invites?api_key=12345...')
    >>>{
            "users": [
                [
                    "admin",
                    11
                ],
                [
                    "user2",
                    0
                ]
            ]
        }

Usage
'''''
*POST* `/api/v1/a/accounts/invites/:username/:count`

Set the invite_ct for the specified user to the specified count

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned.

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/a/accounts/invites/admin/10?api_key=12345...')
    >>>{
           "count": 1,
           "users": [
               {
                   "activated": false,
                   "api_key": "12345",
                   "email": "testing@someting.com",
                   "id": 2,
                   "invite_ct": 0,
                   "invited_by": "admin",
                   "is_admin": false,
                   "last_login": "",
                   "name": null,
                   "password": null,
                   "signup": "2010-04-07 17:50:18",
                   "username": "admin"
               }
           ]
       }


/a/accounts/inactive
--------------------

Usage
'''''
*GET* `/api/v1/a/accounts/inactive`

Return the account info for users that are not set to active. Useful to see
new signups that haven't activated or users with password/reset issues. New
users will have their email address as their username since they've not set
one yet.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned.

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/a/accounts/invites?api_key=12345...')
    >>>{
           "count": 1,
           "users": [
               {
                   "activated": false,
                   "api_key": "12345",
                   "email": "newuser@something.com",
                   "id": 2,
                   "invite_ct": 0,
                   "invited_by": "admin",
                   "is_admin": false,
                   "last_login": "",
                   "name": null,
                   "password": null,
                   "signup": "2011-04-07 17:50:18",
                   "username": "newuser@something.com"
               }
           ]
       }


/admin/readable/todo
--------------------

*GET* `/api/v1/admin/readable/todo`

    Return a list of urls that need to have content fetched for their readable
    views. This is used from external tools that will fetch the content and
    feed back into the api for readable parsing.

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/a/readable/todo?api_key=12345...')
    >>> {
          message: ""
          payload: {
            urls: [
                ...
            ]
          }
          success: true
        }


/admin/readable/statuses
------------------------
@todo
Provide statics of the status code of readable attempts


/admin/readable
---------------
@todo
Provide some readable details, number of outstanding bookmarks to read, number
with readable content, etc.

/admin/:username/deactivate
---------------------------
@todo
Mark a user as disabled. Will not allow them to login, save bookmarks, use the
api


/a/users/list
-------------
Usage
'''''
*GET* `/api/v1/a/users/list`

Return a list of the users in the system.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/a/users/list?api_key=12345...')
    >>>{
            "count": 10,
            "users": [
                [
                    "admin",
                    ...
                ],
                [
                    "user2",
                    ...
                ]
            ]
        }

/a/users/add
------------
Usage
'''''
*POST* `/api/v1/a/users/add`

Admin override and add a new user to the system.

:query param: api_key *required* - the api key for your account to make the call with
:query param: username *required* - the username of the new user
:query param: email *required* - the email address of the new user
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/a/users/list?api_key=12345...', {
        'email': 'test@dummy.com',
        'username': 'test',
    })
    >>>{
           "username": "admin",
           "email": "test@dummy.com",
           "id": 11,
           "random_pass": "blah123",
           ...
       }

/a/users/delete/:username
-------------------------
Usage
'''''
*DELETE* `/api/v1/a/users/delete/:username`

Admin endpoint to remove a user from the system.

Currently meant for bad new user accounts that removes activation and user
account. Does not reach into bmarks/tags.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/a/users/delete/admin?api_key=12345...')
    >>>{
           "success": true,
           "message": "Removed user: admin"
       }


/admin/stats/bmarks
-------------------
GET `/api/v1/admin/stats/bmarks`

    Return the most recent counts of bookmarks, tags, and unique bookmarks

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: count - the number in the result you wish to return
    :query param: page - the page number to get results for based off of the count specified
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/admin/stats/bmarks?api_key=12345...')
    >>> ...


/a/social/twitter_refresh/:username
-------------------
GET `/a/social/twitter_refresh/:username`

    Refresh twitter fetch for specific user

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/a/social/twitter_refresh/admin?api_key=12345...')
    >>> {
            "message": "running bot to fetch user's tweets"
            "success": true,
        }


/a/social/twitter_refresh/all
-------------------
GET `/a/social/twitter_refresh/all`

    Refresh twitter fetch for all the users

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/a/social/twitter_refresh/all?api_key=12345...')
    >>> {
            "message": "running bot to fetch user's tweets"            
            "success": true,
        }

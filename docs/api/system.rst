System wide calls
=================

/bmarks
-------

Usage
''''''
*GET* `/api/v1/bmarks`

Return a list of the most recent bookmarks

:query param: api_key *optional* - the api key for your account to make the call with
:query param: count - the number in the result you wish to return
:query param: page - the page number to get results for based off of the count specified
:query param: with_content - do you wish the readable content of the urls if available
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
''''''''

::

    requests.get('http://127.0.0.1:6543/api/v1/bmarks?count=2&api_key=12345...')
    >>>{
        "count": 2,
        "bmarks": [
            {
                "username": "admin",
                "updated": "2011-07-29 22:23:42",
                "extended": "",
                "description": "Bookie: Recent Bookmarks",
                "tags": [
                    {
                        "tid": 3,
                        "name": "test"
                    },
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 2,
                "stored": "2011-06-21 13:20:26",
                "inserted_by": null,
                "tag_str": "test bookmarks",
                "clicks": 1,
                "hash_id": "c605a21cf19560"
            },
            {
                "username": "admin",
                "updated": "2011-07-15 14:25:16",
                "extended": "Bookie Documentation Home",
                "description": "Bookie Website",
                "tags": [
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 1,
                "stored": "2011-06-20 11:42:47",
                "inserted_by": null,
                "tag_str": "bookmarks",
                "clicks": 1,
                "hash_id": "c5c21717c99797"
            }
        ],
        "tag_filter": null,
        "page": 0,
        "max_count": 10
    }


/bmarks/popular
---------------

Usage
''''''
*GET* `/api/v1/bmarks/popular`

Return a list of the most clicked on bookmarks.

:query param: api_key *optional* - the api key for your account to make the call with
:query param: count - the number in the result you wish to return
:query param: page - the page number to get results for based off of the count specified
:query param: with_content - do you wish the readable content of the urls if available
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
''''''''

::

    requests.get('http://127.0.0.1:6543/api/v1/bmarks/popular?count=2&api_key=12345...')
    >>>{
        "count": 2,
        "bmarks": [
            {
                "username": "admin",
                "updated": "2011-07-29 22:23:42",
                "extended": "",
                "description": "Bookie: Recent Bookmarks",
                "tags": [
                    {
                        "tid": 3,
                        "name": "test"
                    },
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 2,
                "stored": "2011-06-21 13:20:26",
                "inserted_by": null,
                "tag_str": "test bookmarks",
                "clicks": 3,
                "hash_id": "c605a21cf19560",
                "url": "https://bmark.us/recent",
                "total_clicks": 5
            },
            {
                "username": "admin",
                "updated": "2011-07-15 14:25:16",
                "extended": "Bookie Documentation Home",
                "description": "Bookie Website",
                "tags": [
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 1,
                "stored": "2011-06-20 11:42:47",
                "inserted_by": null,
                "tag_str": "bookmarks",
                "clicks": 1,
                "hash_id": "c5c21717c99797",
                "http://docs.bmark.us",
                "total_clicks": 4
            }
        ],
        "tag_filter": null,
        "page": 0,
        "max_count": 10
    }

/bmarks/search/:terms
---------------------

Usage
''''''

*GET* `/api/v1/bmarks/search/:terms`

Return a list of the user's bookmarks based on the fulltext search of the
given terms.  There can be one or more search terms. All search terms are
*OR*'d together. Fulltext search will find matches in the *description*,
*extended*, and *tag_string* fields of a bookmark. You can also perform
fulltext search against the readable content of pages with the correct
query parameter from below.

:query param: api_key *optional* - the api key for your account to make the call with
:query param: count - the number in the result you wish to return
:query param: page - the page number to get results for based off of the count specified
:query param: search_content - include the readable text in the fulltext search.  This can slow down the response.
:query param: with_content - do you wish the readable content of the urls if available
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/bmarks/search/ubuntu?api_key=12345...')
    >>>> {
             "page": null,
             "phrase": "ubuntu",
             "result_count": 2,
             "search_results": [
               {
                 "bid": 3,
                 "clicks": 0,
                 "description": "nickelanddime.png (PNG Image, 1200x1400 pixels) - Scaled (64%)",
                 "extended": "This is the extended description",
                 "hash_id": "adb017923e1f56",
                 "inserted_by": "importer",
                 "stored": "2011-02-25 15:13:00",
                 "tag_str": "nickelanddime kerfuffle banshee amazon ubuntu ubuntu-one canonical",
                 "tags": [
                   {
                     "name": "ubuntu",
                     "tid": 4
                   },
                   {
                     "name": "canonical",
                     "tid": 10
                   }
                 ],
                 "total_clicks": 0,
                 "updated": "",
                 "url": "http://www.ndftz.com/nickelanddime.png",
                 "username": "admin"
               },
               {
                 "bid": 77,
                 "clicks": 0,
                 "description": "My title: ubuntu forum archive about echolinux",
                 "extended": "",
                 "hash_id": "3e9a37d4f7cd74",
                 "inserted_by": "importer",
                 "stored": "2010-07-08 19:30:18",
                 "tag_str": "ham linux",
                 "tags": [
                   {
                     "name": "ham",
                     "tid": 89
                   },
                   {
                     "name": "linux",
                     "tid": 103
                   }
                 ],
                 "total_clicks": 0,
                 "updated": "",
                 "url": "http://ubuntuforums.org/archive/index.php/t-973929.html",
                 "username": "admin"
               }
             ],
             "username": "admin",
             "with_content": false
         }


/suspend
--------

Usage
''''''
*POST* `/api/v1/suspend`

Creates a reset of the account. The user account is locked, an email is
fired to the user's email address on file, and an activation code is
contained within that is required to unlock the account.

:query param: api_key *required* - the api key for your account to make the call with
:query param: email *required* - the email address of the user we're wanting to reset
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 404: Could not find a user for this email address to suspend the account
:error 406: No email address submitted in the request so we can't suspend anyone

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/suspend?api_key=12345...&email=testing@dummy.com')
    >>> {
        "message":  """Your account has been marked for reactivation. Please check your email for instructions to reset your password""",
    }

    requests.post('http://127.0.0.1:6543/api/v1/suspend?api_key=12345...')
    >>> {
        "error":  "Please submit an email address",
    }

    requests.post('http://127.0.0.1:6543/api/v1/suspend?api_key=12345...&email=testing@dummy.com')
    >>> {
        "error":  "You've already marked your account for reactivation.  Please check your email for the reactivation link. Make sure to check your spam folder.",
        "username": admin
    }


Usage
'''''
*DELETE* `/api/v1/suspend`

Reactive the account. Basically we're "deleting the suspend" on the
account. This requires the reactivation key that was sent to the user in
the activation email.

:query param: username - string username of the user we're activating
:query param: activation - string activation code returned emailed from the POST call
:query param: password - a new password to reactivate this account to
:query param: callback - wrap JSON response in an optional callback

Status Codes
'''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 406: The password supplied doesn't satisfy complexity requirements.
:error 500: There was some issue restoring the account. Send for help

Example
''''''''
::

    requests.delete('http://127.0.0.1:6543/api/v1/suspend?api_key=12345&activation=behehe&password=admin')
    >>> {
        "message": "Account activated, please log in",
        "username": "admin"
    }

    requests.delete('http://127.0.0.1:6543/api/v1/suspend?api_key=12345&activation=behehe&password=12')
    >>> {
        "error": "Come on, pick a real password please"
    }


/:username/invite
-----------------

Usage
''''''
*POST* `/api/v1/admin/invite`

Allows a user to create an invitation to another user in the system.

:query param: api_key *required* - the api key for your account to make the call with
:query param: email *required* - the email address of the new user to invite
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 406: No email address submitted in the request so we can't invite anyone

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/invite?api_key=12345...&email=testing@dummy.com')
    >>> {
        "message":  """done""",
    }

    requests.post('http://127.0.0.1:6543/api/v1/admin/invite?api_key=12345...')
    >>> {
        "error":  "Please submit an email address",
    }

    requests.post('http://127.0.0.1:6543/api/v1/admin/invite?api_key=12345...&email=testing@dummy.com')
    >>> {
        "error":  "This user has already been invited to the system.",
        "email": "testing@dummy.com"
    }


/stats/bookmarks
----------------

Usage
'''''

*GET* `/api/v1/stats/bookmarks`

Returns basic statistics about number of bookmarks in the database

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of count, and unique_count

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/stats/bookmarks')
    >>> {
        "count": 115047,
        "unique_count": 108060
    }

/stats/users
------------

Usage
'''''

*GET* `/api/v1/stats/users`

Returns basic statistics about number of users in the database

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of count, activations, and with_bookmarks

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/stats/users')
    >>> {
        "count": 875,
        "activations": 133,
        "with_bookmarks": 388
    }

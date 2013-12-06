About JSON API
------------------
For best performance, and so that we can implement an api that meets the
features we hold important we have our own api you can implement. It's JSON
based and will return a standard JSON response for any call

All api calls should be against `https://$yoursite.com/api/v1`.

Remember, the only authentication method is the api key. If your site is not
hosted behind secure http server then it's likely to get stolen. Please think
about this before setting up a server exposed to the internet.

User specific calls
-------------------

/:username/bmark
~~~~~~~~~~~~~~~~

Usage
'''''
*POST* `/api/v1/admin/bmark`

Submit a new bookmark for storing

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback
:post param: url *required*
:post param: description
:post param: extended
:post param: tags - space separated tag string
:post param: content - html content of the page to readable parse

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 403: if the api key is not valid or missing then this is an unauthorized request

All error responses will have a json body with an error message string and
possibly other helpful information.

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/bmark/admin?api_key=12345...')
    >>> {
            "bmark": {
                "username": "admin",
                "updated": "",
                "extended": "Extended notes",
                "description": "Bookie",
                "tags": [
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 1,
                "stored": "2011-08-06 20:35:54",
                "inserted_by": "unknown_api",
                "tag_str": "bookmarks",
                "clicks": 0,
                "hash_id": "c5c21717c99797"
            },
            "location": "http://localhost/bmark/readable/c5c21717c99797"
        }


/:username/bmark/:hash_id
~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage
'''''
*GET* `/api/v1/admin/bmark/c605a21cf19560`

Get the information about this bookmark.

:query param: api_key *optional* - the api key for your account to make the call with
:query param: with_content - do you wish the readable content of the urls if available
:query param: last_bmark - do you want the information of the last bookmark saved. This is used to supply tag hints in the Chrome extension.
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 404: if the hash id can not be found you'll get a 404
:error 403: if the api key is not valid or missing then this is an unauthorized request

All error responses will have a json body with an error message string and
possibly other helpful information.

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmark/c605a21cf19560?api_key=12345...')
    >>> {
          "bmark": {
            "bid": 2,
            "clicks": 1,
            "description": "Bookie: Recent Bookmarks",
            "extended": "",
            "hash_id": "c605a21cf19560",
            "inserted_by": null,
            "stored": "2011-06-21 13:20:26",
            "tag_str": "test bookmarks",
            "tags": [
              {
                "name": "test",
                "tid": 3
              },
              {
                "name": "bookmarks",
                "tid": 2
              }
            ],
            "updated": "2011-07-29 22:23:42",
            "username": "admin"
          }
        }

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmark/c605a21cf19560?api_key=000')
    >>> {"error": "Not authorized for request."}

Usage
'''''
*POST* `/api/v1/bmark/admin/c605a21cf19560`

Update the stored bookmark with new information.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback
:post param: description
:post param: extended
:post param: tags - space separated tag string
:post param: content - html content of the page to readable parse

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 404: if the hash id can not be found you'll get a 404
:error 403: if the api key is not valid or missing then this is an unauthorized request

All error responses will have a json body with an error message string and
possibly other helpful information.

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/bmark/admin/c605a21cf19560?api_key=12345...')
    >>> {
            "bmark": {
                "username": "admin",
                "updated": "",
                "extended": "Extended notes",
                "description": "Bookie",
                "tags": [
                    {
                        "tid": 2,
                        "name": "bookmarks"
                    }
                ],
                "bid": 1,
                "stored": "2011-08-06 20:35:54",
                "inserted_by": "unknown_api",
                "tag_str": "bookmarks",
                "clicks": 0,
                "hash_id": "c5c21717c99797"
            },
            "location": "http://localhost/bmark/readable/c5c21717c99797"
        }

Usage
'''''
*DELETE* `/api/v1/bmark/admin/c605a21cf19560`

Remove the bookmark from the user's list

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback


Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 404: if the hash id can not be found you'll get a 404
:error 403: if the api key is not valid or missing then this is an unauthorized request

All error responses will have a json body with an error message string and
possibly other helpful information.

Example
'''''''
::

    requests.delete('http://127.0.0.1:6543/api/v1/bmark/admin/c605a21cf19560?api_key=12345...')
    >>> {
          "message": "done",
        }


/:username/bmarks
~~~~~~~~~~~~~~~~~

Usage
''''''
*GET* `/api/v1/admin/bmarks`

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

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmarks?count=2&api_key=12345...')
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


/:username/bmarks/export
~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
''''''
*GET* `/api/v1/admin/bmarks/export`

Get a json dump of all of the bookmarks for a user's account. This will
include all content that we have available. It will take a while to build
and we will be limited this call to only a few times a day at some point.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
'''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmarks/export?api_key=12345...')
    >>> {
          "bmarks": [
            {
              "bid": 1,
              "clicks": 1,
              "description": "Bookie Website",
              "extended": "Bookie Documentation Home",
              "hash_id": "c5c21717c99797",
              "hashed": {
                "clicks": 4,
                "hash_id": "c5c21717c99797",
                "url": "http://bmark.us"
              },
              "inserted_by": null,
              "stored": "2011-06-20 11:42:47",
              "tag_str": "bookmarks",
              "updated": "2011-07-15 14:25:16",
              "username": "admin"
            },
            {
              "bid": 2,
              "clicks": 1,
              "description": "Bookie: Recent Bookmarks",
              "extended": "",
              "hash_id": "c605a21cf19560",
              "hashed": {
                "clicks": 1,
                "hash_id": "c605a21cf19560",
                "url": "https://bmark.us/recent"
              },
              "inserted_by": null,
              "stored": "2011-06-21 13:20:26",
              "tag_str": "test bookmarks",
              "updated": "2011-07-29 22:23:42",
              "username": "admin"
            },
            ...
          ],
          "count": 137,
          "date": "2011-08-08 20:11:43.648699"
        }


/:username/bmarks/popular
~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
''''''
*GET* `/api/v1/admin/bmarks/popular`

Return a list of the most clicked on bookmarks for the user.

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

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmarks/popular?count=2&api_key=12345...')
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


/:username/extension/sync
~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
''''''

*GET* `/api/v1/admin/extension/sync`

This is experimental and very likely to change, so use at your own risk.
We're investigating syncing bookmarks with browsers via their extensions.
This api call will be the trigger point to allow a browser to request all
of the data it needs for loading knowledge of existing bookmarks into a new
browser installation.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request


Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/extension/sync?api_key=12345...')

    >>> {
            "94a2b635d965bc",
            "cf01b934863be8",
            ...
        }


/:username/bmarks/search/:terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
''''''

*GET* `/api/v1/admin/bmarks/search/:terms`

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
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/bmarks/search/ubuntu/linux?api_key=12345...')
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
                     "name": "nickelanddime",
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



/:username/tags/complete
~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
''''''
*GET* `/api/v1/admin/tags/complete`

Return a list of potential tags to use for the given *tag*.

:query param: api_key *optional* - the api key for your account to make the call with
:query param: tag *required* - the part of the word we want completions for
:query param: current - a space separated list of the current tags selected that we should take into account when selecting a potential completion option.
:query param: callback - wrap JSON response in an optional callback

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
''''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/tags/complete?api_key=12345...&tag=ubu')
    >>> {
            current: "",
            tags: [
              "ubuntu",
              "ubuntuone"
            ]
        },


Account Information Calls
--------------------------

/:username/account
~~~~~~~~~~~~~~~~~~

Usage
''''''
*GET* `/api/v1/admin/account`

Return the name and email for the given user account.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
'''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/account?api_key=12345...')
    >>> {
            "username": "admin",
            "name": null,
            "signup": null,
            "activated": true,
            "last_login": null,
            "email": "testing@dummy.com"
        }


Usage
'''''

*POST* `/api/v1/admin/account`

Update the user's name or email address

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback
:post param: name - a new name for the user account
:post param: email - a new email for the user account

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
''''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/account?api_key=12345...')
    >>> {
            "username": "admin",
            "name": null,
            "signup": null,
            "activated": true,
            "last_login": null,
            "email": "testing@dummy.com"
        }


/:username/api_key
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage
'''''

*GET* `/api/v1/admin/api_key`

Fetch the api key for the user from the system. We don't go waving the api
key around so we have to ask for it on its own. Keep this safe. If it's
exposed someone can get at about anything in the system for that user.

I know it's strange to require the api key to get the api key, but hey, you
tell me how to fix it.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback

Status Codes
'''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
''''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/api_key?api_key=12345...')
    >>> {
            "username": "someuser",
            "api_key": "12345..."
        }


/:username/password
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage
'''''
*POST* `/api/v1/admin/account/password`

Change the user's password to the new value provided. Note that the current
password is required to perform the step.

:query param: api_key *required* - the api key for your account to make the call with
:query param: callback - wrap JSON response in an optional callback
:post param: current_password *required* - the current password string from the user
:post param: new_password *required* - the string to change the password to

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: if the api key is not valid or missing then this is an unauthorized request
:error 406: if the new password is not of acceptable strength. We're not letting 2 char passwords to be set, sorry.

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/password?api_key=12345...')
    >>> {
            "username": "someuser",
            "api_key": "12345..."
        }




System wide calls
-----------------

/bmarks
~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Admin only calls
---------------------
These are calls meant to help the admin with the system. Their documented for
the project's need.


/a/accounts/invites
~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~
GET `/api/v1/admin/readable/todo`

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
~~~~~~~~~~~~~~~~~~~~~~~~
@todo
Provide statics of the status code of readable attempts


/admin/readable
~~~~~~~~~~~~~~~
@todo
Provide some readable details, number of outstanding bookmarks to read, number
with readable content, etc.

/admin/:username/deactivate
~~~~~~~~~~~~~~~~~~~~~~~~~~~
@todo
Mark a user as disabled. Will not allow them to login, save bookmarks, use the
api


/a/users/list
~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~
Usage
'''''
*POST* `/api/v1/a/users/add`

Admin override and add a new user to the system.

:query param: api_key *required* - the api key for your account to make the call with
:query param: username *required* - the email address of the new user
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
~~~~~~~~~~~~~~~~~~~~~~~~~~
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




/admin/log
~~~~~~~~~~
GET `/api/v1/admin/log`

    Return the most recent log items from the logging table. Useful for quick
    monitoring.

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: count - the number in the result you wish to return
    :query param: page - the page number to get results for based off of the count specified
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/admin/log?api_key=12345...')
    >>> ...


/admin/stats/bmarks
~~~~~~~~~~~~~~~~~~~
GET `/api/v1/admin/stats/bmarks`

    Return the most recent counts of bookmarks, tags, and unique bookmarks

    :query param: api_key *required* - the api key for your account to make the call with
    :query param: count - the number in the result you wish to return
    :query param: page - the page number to get results for based off of the count specified
    :query param: callback - wrap JSON response in an optional callback

::

    requests.get('http://127.0.0.1:6543/api/v1/admin/stats/bmarks?api_key=12345...')
    >>> ...




Delicious API
--------------
Since we started out attempting to match the Delicious api, we support some of
those features. Not all of them make sense, so not all are implemented.
Currently, the browser extensions communicate to the server via the Delicious
api calls. Eventually, we'll probably move those over to the official JSON api
as I much prefer JSON and hate dealing with the XML calls that Delicious
implemented.

All of our api calls are POST since we allow for some large content payloads.

API Key
~~~~~~~
All of our delicious.com api calls that make changes to the database, require
an `api_key` parameter to be passed with the request. This is a slight
deviation from the Delicious API since we do not currently support login.

Available API Calls
~~~~~~~~~~~~~~~~~~~~
`/delapi/posts/add`:
    See: http://www.delicious.com/help/api#posts_add We also support an extra
    parameter `content` that is html content for the bookmark you'd like parsed
    and stored as its readable content. The Chrome extension currently supports
    this as an option and is meant to help provide readable content immediately
    vs whenever a cron script can fetch and load a page.

`/delapi/posts/delete`:
    See: http://www.delicious.com/help/api#posts_delete Other than the
    `api_key` parameter this is just pass a url and it'll get deleted.

`/delapi/posts/get`:
    See: http://www.delicious.com/help/api#posts_get We only support passing a
    `url` and do not support getting by tag, hash, etc. This does not require
    an `api_key` since there are no changes to the database to be made.

`/delapi/tags/complete`:
    This is not an delicious api call, but is currently stored in here. It's
    meant for providing tag autocomplete options to a widget based on current
    input. You must pass a `tag` with the characters entered so far. It also
    optionally supports a `current_tags` parameter so that completion will take
    into account existing tags. You can see this in action at the demo site tag
    filter at http://bmark.us

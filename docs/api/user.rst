User specific calls
===================

/:username/bmark
----------------

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
:post param: content - html content of the page to be parsed as the readable version. if not provided, will be rendered by the celery job at some point in the future (or never if celery is not running).
:post param: is_private - specifies whether the bookmark is private or not. By default the bookmarks are stored as private

Status Codes
''''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 403: if the api key is not valid or missing then this is an unauthorized request

All error responses will have a json body with an error message string and
possibly other helpful information.

Example
'''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/bmark?api_key=12345...')
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
                "is_private": true,
                "tag_str": "bookmarks",
                "clicks": 0,
                "hash_id": "c5c21717c99797"
            },
            "location": "http://localhost/bmark/readable/c5c21717c99797"
        }


/:username/bmark/:hash_id
-------------------------
Usage
'''''
*GET* `/api/v1/admin/bmark/c605a21cf19560`

Get the information about this bookmark.

:query param: api_key *optional* - the api key for your account to make the call with
:query param: with_content - do you wish the readable content of the urls if available
:query param: url - This is the url of the page that you are trying to bookmark.This is used to supply tags in the Chrome extension.
:query param: description - This is the title of the page.This is used to supply tags in the Chrome extension.
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
            "is_private": true,
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
                "is_private": true,
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
-----------------

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
                "is_private": true,
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
                "is_private": true,
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
------------------------

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
              "is_private": true,
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
              "is_private": true,
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
-------------------------

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
                "is_private": true,
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
                "is_private": true,
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
-------------------------

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
-------------------------------

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
:query param: with_content - include the readable text in the fulltext search.  This can slow down the response.
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
                 "is_private": true,
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
                 "is_private": true,
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


/:username/social_connections/
---------------------------

Usage
''''''
*GET* `/api/v1/admin/social_connections/`

Get a json dump of the social connections count for a user's account, usernames
used in the social connections and refresh date i.e last time respective bot 
parsed the data from the social connection.

:query param: api_key *required* - the api key for your account to make the call with

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/social_connections/api_key=12345..')
    >>> {
            "count": 2
            "social_connections": [{
             "username": "admin", 
             "last_connection": "2014-06-12 17:39:41.855184",
             "uid": "1234",
             "type": "TwitterConnection"
             "twitterConnection": {
                "twitter_username": "bookie",
                "refresh_date": "2014-06-12 17:39:41.855202"
             }
            },{
             "username": "admin", 
             "last_connection": "2014-06-12 17:41:09.720954",
             "uid": "1234",
             "type": "TwitterConnection"
             "twitterConnection": {
                  "twitter_username": "bookie",
                  "refresh_date": "2014-06-12 17:41:09.720954"
              }
            }]
        }


/:username/stats/bmarkcount
---------------------------

Usage
''''''
*GET* `/api/v1/admin/stats/bmarkcount`

Get a json dump of the bookmark count for a user's account for a time period.
The time period can be specified or else a json dump of the bookmark count of
the past 30 days will be returned.  If the start_date is specified to be the
first day of the month and the end_date is not supplied, a json response of
the bookmark count of the whole month will be returned.

:query param: api_key *required* - the api key for your account to make the call with
:query param: start_date *optional* - Find the bookmark count in the specified time window,
              beginning with start_date.
:query param: end_date *optional* - Find the bookmark count in the specified time window,
              ending with end_date.

Status Codes
''''''''''''
:success 200: If successful a "200 OK" will be returned
:error 403: if the api key is not valid or missing then this is an unauthorized request

Example
'''''''
::

    requests.get('http://127.0.0.1:6543/api/v1/admin/stats/bmarkcount?start_date=2014-03-01&end_date=2014-03-05&api_key=12345..')
    >>> {
            "count": [
              {
                "attrib": "user_bookmarks_admin",
                "data": 0,
                "id": 1,
                "tstamp": "2014-03-02 20:50:52"
              },
              {
                "attrib": "user_bookmarks_admin",
                "data": 3,
                "id": 10,
                "tstamp": "2014-03-03 20:50:52"
              },
              {
                "attrib": "user_bookmarks_admin",
                "data": 5,
                "id": 21,
                "tstamp": "2014-03-04 20:50:52"
              }
            ]
        }


/:username/tags/complete
------------------------

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

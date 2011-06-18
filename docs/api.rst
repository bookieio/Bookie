============
Bookie API
============

Bookie supports making calls to the system in a pair of ways.

Official JSON API
------------------
For best performance and so that we can implement an api that meets the
features we hold important we have our own api you can implement. It's JSON
based and will return a standard JSON response for any call

All api calls should be against `http://$yoursite.com/api/v1`. From this point
forward, all urls are expected to be rooted off of this url. So when you see
`/bmarks/recent` you know the url is `http://$yoursite.com/api/v1/bmarks/recent`.

Response Description
~~~~~~~~~~~~~~~~~~~~
::

    // sample api call object
    {
        "message": "",
        "payload": {},
        "success": true
    }

success:
    Success will be a boolean if the call was successful or not. If falst, this
    just means that while the http call was correct, it failed for some reason.
    Perhaps you were missing a parameter in the call? Perhaps a record was not
    found. Check the `message` value for more information

message:
    Message will help describe details on the current api call. On most
    occassions, it will be empty on a successful call, and it will have some
    details for an api call with `success: false`.

payload:
    Any data requested will be included in the payload. It's a nested object
    and will vary depending on the api call in question. If there is any
    generated html to return, it will be in the root of `payload` and available
    as `payload.html`. This is kept consistent to help with writing JavaScript
    to automatically load html content from AJAX api calls.


Available API Calls
~~~~~~~~~~~~~~~~~~~~

`/bmarks/recent`:
    This will return a list of the most recent bookmarks added to the system in
    descending order. Each bookmark returned will be contain the information
    from the main bookmark table and does not contain information of related
    tables stored such as the `readable` table.

`/bmarks/popular`:
    This will return a list of the most popular bookmarks in the system as
    determined by the click counter implemented in the `bmarks` table.  Each
    bookmark returned will be contain the information from the main bookmark
    table and does not contain information of related tables stored such as the
    `readable` table.

`/bmarks/search/$term1/$term2`:
    Search will return a set of results for a query based on `OR` of the terms
    requested. Each term is expected to be added as a part of the url as
    `/term1/term2/term3`. This search will check against a bookmarks
    `description`, `extended`, and `tag_str` data. Again, each bookmark
    returned will be contain the information from the main bookmark table and
    does not contain information of related tables stored such as the
    `readable` table.

`/bmarks/$hash_id`:
    Will return the detailed information for a single bookmark in the system.
    This query is based on the `hash_id` parameter of the bookmark. Generally,
    you'd fetch a list of the bookmarks via the `recent` or `popular` api calls
    and then allow the user to select a single bookmark via the generated
    `hash_id`. This will include all data from the `bmarks` table as well as a
    `item.readable` object that will include the readable content for the
    bookmark.

`/bmarks/sync`:
    This is experimental and very likely to change, so use at your own risk.
    We're investigating syncing bookmarks with browsers via their extensions.
    This api call will be the trigger point to allow a browser to request all
    of the data it needs for loading knowledge of existing bookmarks into a new
    browser installation.

`/bmarks/add`:
    A POST call to add a new bookmark to the system. This is validated by
    passing the `api_key` parameter to the server in the POST.

`/bmarks/remove/$url`
    Remove the bookmark and content for this url. This might change and require
    a `hash_id` instead of a url in the future.

`/tags/complete`?tag=$str&current=test%20tags
    Provides a list of possible completion strings for the given partial `tag`
    string. For instance, if `tag` where 'py' then it might return "python",
    "pylint". `current` is an optional space separated list of current tags to
    provide context. In this way, the completion will only provide tags that
    also occur on bookmarks with the list of current tags as well.



Paging through results
~~~~~~~~~~~~~~~~~~~~~~~
All of the api calls that return a list of results are setup for paging. The
default in the system is 50 results, and the mobile interface is currently
setup to fetch in sets of 10. In order to request another set of results, you
just need to pass the `count` and `page` numbers you wish to fetch as query
parameters.

So a sample api call for the 3rd page of results to `/bmarks/recent` would look
like: (no page is 0 based)

::

    http://bmark.us/{username}/api/v1/bmarks/recent?count=20&page=2


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

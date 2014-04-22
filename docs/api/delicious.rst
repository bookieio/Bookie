Delicious API
=============

Since we started out attempting to match the Delicious api, we support some of
those features. Not all of them make sense, so not all are implemented.
Currently, the browser extensions communicate to the server via the Delicious
api calls. Eventually, we'll probably move those over to the official JSON api
as I much prefer JSON and hate dealing with the XML calls that Delicious
implemented.

All of our api calls are POST since we allow for some large content payloads.

API Key
-------
All of our delicious.com api calls that make changes to the database, require
an `api_key` parameter to be passed with the request. This is a slight
deviation from the Delicious API since we do not currently support login.

Available API Calls
-------------------
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

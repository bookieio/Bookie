Account Information Calls
=========================

/:username/account
------------------

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
------------------
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

/:username/api_key
------------------
Usage
'''''

*POST* `/api/v1/admin/reset_api_key`

Request a brand new API key. The old API key will be invalidated.
A new key will be generated and tied to your account.
Please do not forget to update the API key in the browser extensions and
other places where the API is used.

:post param: api_key *required* - the api key for your account to make the call with
:post param: username *required* - the username whose api key has to be reset

Status Codes
'''''''''''''
:success 200: If successful a "200 OK" will be returned, with json body of message: done
:error 403: If the api key is not valid or missing then this is an unauthorized request

Example
''''''''
::

    requests.post('http://127.0.0.1:6543/api/v1/admin/api_key?api_key=12345...')
    >>> {
            "api_key": "98765...",
            "message": "API key was..."
        }

/:username/password
-------------------

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

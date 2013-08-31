"""Handle auth and authz activities in bookie"""
import logging

from decorator import decorator
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from bookie.models.auth import UserMgr

LOG = logging.getLogger(__name__)


class AuthHelper(object):
    """Manage the inner workings of authorizing things"""

    @staticmethod
    def check_api(submitted_key, users_key):
        """Verify the api key is valid"""
        if users_key != submitted_key:
            return False
        else:
            return True

    @staticmethod
    def check_login(request, username=None):
        """Check that the user is logged in correctly

        :param username: a username to make sure the current user is in fact

        """
        if request.user is None:
            return False

        # if we have a username we're told to check against, make sure the
        # username matches
        if username is not None and username != request.user.username:
            return False

        return True

    @staticmethod
    def not_valid(request, redirect=None):
        """Handle the Forbidden exception unless redirect is there

        The idea is that if there's a redirect we shoot them to the login form
        instead

        """
        if redirect is None:
            raise HTTPForbidden('Deactivated Account')
        else:
            raise HTTPFound(location=request.route_url(redirect))


class ReqOrApiAuthorize(object):
    """A context manager that works with either Api key or logged in user"""

    def __init__(self, request, api_key, user_acct, username=None,
                 redirect=None):
        self.request = request
        self.api_key = api_key
        self.user_acct = user_acct
        self.username = username

        if redirect:
            self.redirect = redirect

    def __enter__(self):
        """Handle the verification side

        Logged in user checked first, then api matching

        """

        # if the user account is not activated then no go
        if not self.user_acct.activated:
            raise HTTPForbidden('Deactivated Account')

        if AuthHelper.check_login(self.request, username=self.username):
            return True

        if AuthHelper.check_api(self.api_key, self.user_acct.api_key):
            return True

        raise HTTPForbidden('Invalid Authorization')

    def __exit__(self, exc_type, exc_value, traceback):
        """No cleanup to do here"""
        pass


class ApiAuthorize(object):
    """Context manager to check if the user is authorized

    use:
        with ApiAuthorize(some_key):
            # do work

    Will return NotAuthorized if it fails

    """

    def __init__(self, user, submitted_key, redirect=None):
        """Create the context manager"""
        self.user = user


class RequestWithUserAttribute(Request):
    @reify
    def user(self):
        # <your database connection, however you get it, the below line
        # is just an example>
        # dbconn = self.registry.settings['dbconn']
        user_id = unauthenticated_userid(self)
        if user_id is not None:
            # this should return None if the user doesn't exist
            # in the database
            user = UserMgr.get(user_id=user_id)
            return user

    def __enter__(self):
        """Verify api key set in constructor"""
        # if the user account is not activated then no go
        if not self.user.activated:
            raise HTTPForbidden('Deactivated Account')

        if not AuthHelper.check_api(self.check_key, self.user.api_key):
            raise HTTPForbidden('Invalid Authorization')

    def __exit__(self, exc_type, exc_value, traceback):
        """No cleanup work to do after usage"""
        pass


class ReqAuthorize(object):
    """Context manager to check if the user is logged in

    use:
        with ReqAuthorize(request):
            # do work

    Will return NotAuthorized if it fails

    """

    def __init__(self, request, username=None, redirect=None):
        """Create the context manager"""
        self.request = request
        self.username = username
        self.redirect = redirect

    def __enter__(self):
        """Verify api key set in constructor"""
        if not AuthHelper.check_login(self.request, self.username):
            raise HTTPForbidden('Invalid Authorization')

    def __exit__(self, exc_type, exc_value, traceback):
        """No cleanup work to do after usage"""
        pass


class api_auth():
    """View decorator to set check the client is permitted

    Since api calls can come from the api via a api_key or a logged in user via
    the website, we need to check/authorize both

    If this is an api call and the api key is valid, stick the user object
    found onto the request.user so that the view can find it there in one
    place.

    """

    def __init__(self, api_field, user_fetcher, admin_only=False, anon=False):
        """
        :param api_field: the name of the data in the request.params and the
                          User object we compare to make sure they match
        :param user_fetcher: a callable that I can give a username to and
                             get back the user object

        :sample: @ApiAuth('api_key', UserMgr.get)

        """
        self.api_field = api_field
        self.user_fetcher = user_fetcher
        self.admin_only = admin_only
        self.anon = anon

    def __call__(self, action_):
        """ Return :meth:`wrap_action` as the decorator for ``action_``. """
        return decorator(self.wrap_action, action_)

    def _check_admin_only(self, request):
        """If admin only, verify current api belongs to an admin user"""
        api_key = request.params.get(self.api_field, None)

        if request.user is None:
            user = self.user_fetcher(api_key=api_key)
        else:
            user = request.user

        if user is not None and user.is_admin:
            request.user = user
            return True

    def wrap_action(self, action_, *args, **kwargs):
        """
        Wrap the controller action ``action_``.

        :param action_: The controller action to be wrapped.

        ``args`` and ``kwargs`` are the positional and named arguments which
        will be passed to ``action_`` when called.

        """
        # check request.user to see if this is a logged in user
        # if so, then make sure it matches the matchdict user

        # request should be the one and only arg to the view function
        request = args[0]
        username = request.matchdict.get('username', None)
        api_key = None

        # if this is admin only, you're either an admin or not
        if self.admin_only:
            if self._check_admin_only(request):
                return action_(*args, **kwargs)
            else:
                request.response.status_int = 403
                return {'error': "Not authorized for request."}

        if request.user is not None:
            if AuthHelper.check_login(request, username):
                # then we're good, this is a valid user for this url
                return action_(*args, **kwargs)

        # get the user the api key belongs to
        if self.api_field in request.params:
            # we've got a request with url params
            api_key = request.params.get(self.api_field, None)
            username = request.params.get('username', username)

        def is_json_auth_request(request):
            if hasattr(request, 'json_body'):
                if self.api_field in request.json_body:
                    return True
            return False

        if is_json_auth_request(request):
            # we've got a ajax request with post data
            api_key = request.json_body.get(self.api_field, None)
            username = request.json_body.get('username', None)

        if username is not None and api_key is not None:
            # now get what this user should be based on the api_key
            request.user = self.user_fetcher(api_key=api_key)

            # if there's a username in the url (rdict) then make sure the user
            # the api belongs to is the same as the url. You can't currently
            # use the api to get info for other users.
            if request.user and request.user.username == username:
                return action_(*args, **kwargs)

        # if this api call accepts anon requests then let it through
        if self.anon:
            return action_(*args, **kwargs)

        # otherwise, we're done, you're not allowed
        request.response.status_int = 403
        return {'error': "Not authorized for request."}

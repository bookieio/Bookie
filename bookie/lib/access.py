"""Handle auth and authz activities in bookie"""
import logging

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
            LOG.error('Invalid API Key! {0} v {1}'.format(users_key,
                                                          submitted_key))
            return False
        else:
            return True

    @staticmethod
    def check_login(request, username=None):
        """Check that the user is logged in correctly

        :param username: a username to make sure the current user is in fact

        """
        if request.user is None:
            LOG.error('Invalid Request: Not Logged in!')
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
            LOG.debug('Redirecting to: ' + redirect)
            raise HTTPFound(location=request.route_url(redirect))


class ReqOrApiAuthorize(object):
    """A context manager that works with either Api key or logged in user"""

    def __init__(self, request, api_key, user_acct, username=None, redirect=None):
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
            LOG.debug("API call with deactivated account")
            raise HTTPForbidden('Deactivated Account')

        if AuthHelper.check_login(self.request, username=self.username):
            LOG.debug("CHECK LOGIN SUCCESS")
            return True

        if AuthHelper.check_api(self.api_key, self.user_acct.api_key):
            LOG.debug("CHECK API SUCCESS")
            return True

        LOG.debug("FAILED AUTH CHECKS")
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
        self.api_key = user.api_key
        self.check_key = submitted_key

        if redirect:
            self.redirect = redirect

    def __enter__(self):
        """Verify api key set in constructor"""
        # if the user account is not activated then no go
        if not self.user.activated:
            LOG.debug("API only call with deactivated account")
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


class RequestWithUserAttribute(Request):
    @reify
    def user(self):
        # <your database connection, however you get it, the below line
        # is just an example>
        # dbconn = self.registry.settings['dbconn']
        LOG.debug('in Request with Attribute')
        user_id = unauthenticated_userid(self)
        LOG.debug(user_id)
        if user_id is not None:
            LOG.debug('user_id is not none')

            # this should return None if the user doesn't exist
            # in the database
            user = UserMgr.get(user_id=user_id)
            LOG.debug(user)
            return user

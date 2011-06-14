"""Handle auth and authz activities in bookie"""
import logging

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from bookie.models.auth import UserMgr


LOG = logging.getLogger(__name__)


class ApiAuthorize(object):
    """Context manager to check if the user is authorized

    use:
        with ApiAuthorize(some_key):
            # do work

    Will return NotAuthorized if it fails

    """

    def __init__(self, submitted_key, config_key):
        """Create the context manager"""
        self.api_key = config_key
        self.check_key = submitted_key

    def __enter__(self):
        """Verify api key set in constructor"""
        if self.api_key != self.check_key:
            LOG.error('Invalid API Key! {0} v {1}'.format(self.api_key,
                                                          self.check_key))
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

    def __init__(self, request, username=None):
        """Create the context manager"""
        self.request = request
        self.username = username

    def __enter__(self):
        """Verify api key set in constructor"""
        if self.request.user is None or self.request.user.username is None:
            LOG.error('Invalid Request: Not Logged in!')
            raise HTTPForbidden('Invalid Authorization')

        # if we have a username we're told to check against, make sure the
        # username matches
        if self.username != self.request.user.username:
            LOG.error('Invalid Request: Wring Username!')
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

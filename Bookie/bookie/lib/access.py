"""Handle auth and authz activities in bookie"""
import logging

from pyramid.httpexceptions import HTTPForbidden
from pyramid.settings import asbool

LOG = logging.getLogger(__name__)


class Authorize(object):
    """Context manager to check if the user is authorized

    use:
        with Authorize(some_key):
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

def edit_enabled(settings):
    """Is the config .ini setting for allowing edit enabled?

    If the .ini setting for ui edits is not true, then no authed

    """
    allow_edit = asbool(settings.get('allow_edit', False))

    if allow_edit:
        return True
    else:
        return False



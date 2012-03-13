"""Test the limited signup process

"""
import logging

from nose.tools import eq_
from nose.tools import ok_
from pyramid import testing
from unittest import TestCase

from bookie.models import DBSession
from bookie.models.auth import Activation
from bookie.models.auth import User


LOG = logging.getLogger(__name__)

class TestInviteSetup(TestCase):
    """Verify we have/can work with the invite numbers"""

    def testHasNoInvites(self):
        """Verify that if the user has no invites, they can't invite"""
        u = User()
        u.invite_ct = 0
        ok_(not u.has_invites(), 'User should have no invites')
        ok_(not u.invite('me@you.com'), 'Should not be able to invite a user')

    def testInviteCreatesUser(self):
        """We should get a new user when inviting something"""



class TestSigningUpUser(TestCase):
    """Start out by verifying a user starts out in the right state"""

    def testInitialUserInactivated(self):
        """A new user signup should be a deactivated user"""
        u = User()
        DBSession.add(u)

        eq_(False, u.activated,
            'A new signup should start out deactivated by default')
        ok_(u.activation.code is not None,
            'A new signup should start out as deactivated')
        eq_('signup', u.activation.created_by,
            'This is a new signup, so mark is as thus')

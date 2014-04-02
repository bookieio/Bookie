"""Test the limited signup process

"""
import logging
from urllib import (
    quote,
    urlencode,
)
import transaction

from bookie.models import DBSession
from bookie.models.auth import Activation
from bookie.models.auth import User
from bookie.models.auth import UserMgr

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests import TestViewBase


LOG = logging.getLogger(__name__)


class TestInviteSetup(TestDBBase):
    """Verify we have/can work with the invite numbers"""

    def testHasNoInvites(self):
        """Verify that if the user has no invites, they can't invite"""
        u = User()
        u.invite_ct = 0
        self.assertFalse(u.has_invites(), 'User should have no invites')
        self.assertFalse(
            u.invite('me@you.com'), 'Should not be able to invite a user')

    def testInviteCreatesUser(self):
        """We should get a new user when inviting something"""
        me = User()
        me.username = u'me'
        me.email = u'me.com'
        me.invite_ct = 2
        you = me.invite(u'you.com')

        self.assertEqual(
            'you.com',
            you.username,
            'The email should be the username')
        self.assertEqual(
            'you.com',
            you.email,
            'The email should be the email')
        self.assertTrue(
            len(you.api_key),
            'The api key should be generated for the user')
        self.assertFalse(
            you.activated,
            'The new user should not be activated')
        self.assertEqual(
            1,
            me.invite_ct,
            'My invite count should be deprecated')


class TestSigningUpUser(TestDBBase):
    """Start out by verifying a user starts out in the right state"""

    def testInitialUserInactivated(self):
        """A new user signup should be a deactivated user"""
        u = User()
        u.email = gen_random_word(10)
        DBSession.add(u)

        self.assertEqual(
            False,
            u.activated,
            'A new signup should start out deactivated by default')
        self.assertTrue(
            u.activation.code is not None,
            'A new signup should start out as deactivated')
        self.assertEqual(
            'signup',
            u.activation.created_by,
            'This is a new signup, so mark is as thus')


class TestOpenSignup(TestViewBase):
    """New users can request a signup for an account."""

    def tearDown(self):
        super(TestOpenSignup, self).tearDown()
        User.query.filter(User.email == u'testing@newuser.com').delete()

    def testSignupRenders(self):
        """A signup form is kind of required."""
        res = self.app.get('/signup')

        self.assertIn('Sign up for Bookie', res.body)
        self.assertNotIn('class="error"', res.body)

    def testEmailRequired(self):
        """Signup requires an email entry."""
        res = self.app.post('/signup_process')
        self.assertIn('Please supply', res.body)

    def testEmailAlreadyThere(self):
        """Signup requires an email entry."""
        res = self.app.post(
            '/signup_process',
            params={
                'email': 'testing@dummy.com'
            }
        )
        self.assertIn('already signed up', res.body)

    def testEmailIsLowercase(self):
        """Signup saves email as all lowercase"""
        res = self.app.post(
            '/signup_process',
            params={
                'email': 'CAPITALTesting@Dummy.cOm'
            }
        )
        self.assertIn('capitaltesting@dummy.com', res.body)

    def testUsernameAlreadyThere(self):
        """Signup requires an unique username entry."""
        email = 'testing@gmail.com'
        new_user = UserMgr.signup_user(email, u'invite')
        DBSession.add(new_user)

        transaction.commit()

        user = DBSession.query(User).filter(User.username == email).one()

        url = quote('/{0}/reset/{1}'.format(
            user.email,
            user.activation.code
        ))

        res = self.app.post(
            url,
            params={
                'password': u'testing',
                'username': user.username,
                'code': user.activation.code,
                'new_username': u'admin',
            })
        self.assertIn('Username already', res.body)

    def testResetFormDisplay(self):
        """Make sure you can GET the reset form."""
        email = 'testing@gmail.com'
        new_user = UserMgr.signup_user(email, u'invite')
        DBSession.add(new_user)

        transaction.commit()

        user = DBSession.query(User).filter(User.username == email).one()

        url = quote('/{0}/reset/{1}'.format(
            user.email,
            user.activation.code
        ))

        res = self.app.get(url)
        self.assertIn('Activate', res.body)

    def testUsernameIsLowercase(self):
        """Signup saves username as all lowercase"""
        email = 'TestingUsername@test.com'
        new_user = UserMgr.signup_user(email, u'testcase')
        DBSession.add(new_user)

        transaction.commit()

        user = DBSession.query(User).filter(
            User.username == email.lower()).one()

        params = {
            'password': u'testing',
            'username': user.username,
            'code': user.activation.code,
            'new_username': 'TESTLowercase'
        }
        url = '/api/v1/suspend?' + urlencode(params, True)

        # Activate the user, setting their new username which we want to
        # verify does get lower cased during this process.
        self.app.delete(url)

        user = DBSession.query(User).filter(User.email == email.lower()).one()
        self.assertIn('testlowercase', user.username)

    def testSignupWorks(self):
        """Signing up stores an activation."""
        email = u'testing@newuser.com'
        UserMgr.signup_user(email, u'testcase')

        activations = Activation.query.all()

        self.assertTrue(len(activations) == 1)
        act = activations[0]

        self.assertEqual(
            email,
            act.user.email,
            "The activation email is the correct one.")

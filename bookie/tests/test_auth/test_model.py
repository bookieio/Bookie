"""Test the Auth model setup"""
from unittest import TestCase
from pyramid import testing

from datetime import (
    datetime,
    timedelta,
)

from bookie.models import DBSession
from bookie.models.auth import Activation
from bookie.models.auth import User
from bookie.models.auth import UserMgr

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestPassword(TestCase):
    """Test password checks"""
    pass


class TestAuthUser(TestCase):
    """Test User Model"""
    test_hash = '$2a$10$FMFKEYqC7kifFTm05iag7etE17Q0AyKvtX88XUdUcM7rvpz48He92'
    test_password = 'testing'

    def test_password_set(self):
        """Make sure we get the proper hashed password"""
        tst = User()
        tst.password = self.test_password

        self.assertEqual(
            len(tst.password),
            60,
            "Hashed should be 60 char long: " + tst.password)
        self.assertEqual(
            '$2a$',
            tst.password[:4],
            "Hash should start with the right complexity: " + tst.password[:4])

    def test_password_match(self):
        """Try to match a given hash"""

        tst = User()
        tst._password = self.test_hash

        self.assertTrue(
            tst._password == self.test_hash, "Setting should have hash")
        self.assertTrue(
            tst.password == self.test_hash, "Getting should have hash")
        self.assertTrue(
            tst.validate_password(self.test_password),
            "The password should pass against the given hash: " + tst.password)


class TestAuthUserDB(TestDBBase):
    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        empty_db()

    def test_activation_delete(self):
        """Make sure removing an activation does not remove a user."""
        tst = User()
        tst.username = gen_random_word(10)
        tst.activation = Activation(u'signup')
        DBSession.add(tst)
        DBSession.flush()

        DBSession.delete(tst.activation)

        users = UserMgr.get_list()

        # We still have the admin user as well so the count is two.
        self.assertEqual(
            2,
            len(users),
            'We should have a total of 2 users still: ' + str(len(users)))

    def test_activation_cascade(self):
        """Removing a user cascades the activations as well."""
        tst = User()
        tst.username = gen_random_word(10)
        tst.activation = Activation(u'signup')
        DBSession.add(tst)
        DBSession.flush()

        DBSession.delete(tst)

        users = UserMgr.get_list()

        # We still have the admin user as well so the count is one.
        self.assertEqual(
            1,
            len(users),
            'We should have a total of 1 user still: ' + str(len(users)))

        activations = DBSession.query(Activation).all()
        self.assertEqual(
            0, len(activations), 'There should be no activations left')

    def test_non_activated_account(self):
        """Removing a non activated account"""
        # When all the conditions are satisfied, the account should be deleted.
        email = u'testingdelete@gmail.com'
        UserMgr.signup_user(email, u'testcase')
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            1,
            len(activations),
            'We should have a total of 1 activation: ' + str(len(activations)))
        self.assertEqual(
            2,
            len(users),
            'We should have a total of 2 users: ' + str(len(users)))
        activations[0].valid_until = datetime.utcnow() - timedelta(days=35)
        UserMgr.non_activated_account(delete=True)
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            0,
            len(activations),
            'There should be no activations left')
        self.assertEqual(
            1,
            len(users),
            'We should have a total of 1 user still: ' + str(len(users)))
        # When the account is activated, it should not be deleted.
        email = u'testingactivated@gmail.com'
        UserMgr.signup_user(email, u'testcase')
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            1,
            len(activations),
            'We should have a total of 1 activation: ' + str(len(activations)))
        self.assertEqual(
            2,
            len(users),
            'We should have a total of 2 users: ' + str(len(users)))
        users[1].activated = True
        UserMgr.non_activated_account(delete=True)
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            1,
            len(activations),
            'We should have a total of 1 activation still')
        self.assertEqual(
            2,
            len(users),
            'We should have a total of 2 users still: ' + str(len(users)))
        # When the account last login is not None, it should not be deleted.
        # This happens when a user forgets his/her password.
        email = u'testinglastlogin@gmail.com'
        UserMgr.signup_user(email, u'testcase')
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            2,
            len(activations),
            'We should have a total of 2 activations')
        self.assertEqual(
            3,
            len(users),
            'We should have a total of 3 users: ' + str(len(users)))
        users[2].last_login = datetime.utcnow()
        UserMgr.non_activated_account(delete=True)
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            2,
            len(activations),
            'We should have a total of 2 activations still')
        self.assertEqual(
            3,
            len(users),
            'We should have a total of 3 users still: ' + str(len(users)))
        # The account should not be deleted before 30 days since signup.
        email = u'testingdays@gmail.com'
        UserMgr.signup_user(email, u'testcase')
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            3,
            len(activations),
            'We should have a total of 3 activations')
        self.assertEqual(
            4,
            len(users),
            'We should have a total of 4 users: ' + str(len(users)))
        UserMgr.non_activated_account(delete=True)
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            3,
            len(activations),
            'We should have a total of 3 activations still')
        self.assertEqual(
            4,
            len(users),
            'We should have a total of 4 users still')
        # The account details should be shown if it is not asked to delete.
        email = u'testingdetails@gmail.com'
        UserMgr.signup_user(email, u'testcase')
        activations = Activation.query.all()
        users = User.query.all()
        self.assertEqual(
            4,
            len(activations),
            'We should have a total of 4 activations')
        self.assertEqual(
            5,
            len(users),
            'We should have a total of 5 users: ' + str(len(users)))
        account_signup = datetime.utcnow() - timedelta(days=35)
        activations[3].valid_until = account_signup
        account_details = UserMgr.non_activated_account(delete=False)
        self.assertEqual(
            email,
            account_details[0].email)
        self.assertEqual(
            False,
            account_details[0].activated)
        self.assertEqual(
            u'testcase',
            account_details[0].invited_by)


class TestAuthMgr(TestCase):
    """Test User Manager"""

    def test_get_id(self):
        """Fetching user by the id"""
        # the migration adds an initial admin user to the system
        user = UserMgr.get(user_id=1)
        self.assertEqual(
            user.id,
            1,
            "Should have a user id of 1: " + str(user.id))
        self.assertEqual(
            user.username,
            'admin',
            "Should have a username of admin: " + user.username)

    def test_get_username(self):
        """Fetching the user by the username"""
        user = UserMgr.get(username=u'admin')
        self.assertEqual(
            user.id,
            1,
            "Should have a user id of 1: " + str(user.id))
        self.assertEqual(
            user.username,
            'admin',
            "Should have a username of admin: " + user.username)

    def test_get_bad_user(self):
        """We shouldn't get a hit if the user is inactive"""
        user = UserMgr.get(username=u'noexist')

        self.assertEqual(
            user,
            None,
            "Should not find a non-existant user: " + str(user))

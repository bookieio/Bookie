"""Test the Auth model setup"""
from unittest import TestCase
from pyramid import testing


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

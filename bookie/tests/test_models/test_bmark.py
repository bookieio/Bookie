"""Test the basics including the bmark and tags"""

from pyramid import testing

from bookie.models import (
    DBSession,
    Bmark,
)
from bookie.models.auth import User

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestBmark(TestDBBase):
    """Handle bmark function checks"""

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

    def test_has_access_same_user_public(self):
        """Test that a user can view their own public bookmark"""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        b = Bmark(
            url=gen_random_word(12),
            username=user.username,
            is_private=False,
        )
        b.hash_id = gen_random_word(3)
        DBSession.add(b)
        res = b.has_access(user.username)
        self.assertEqual(True, res)

    def test_has_access_same_user_private(self):
        """Test that a user can view their own private bookmark"""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        b = Bmark(
            url=gen_random_word(12),
            username=user.username,
            is_private=True,
        )
        b.hash_id = gen_random_word(3)
        DBSession.add(b)
        res = b.has_access(user.username)
        self.assertEqual(True, res)

    def test_has_access_diff_user_public(self):
        """Test that a different user can view another's public bookmark"""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        b = Bmark(
            url=gen_random_word(12),
            username=gen_random_word(10),
            is_private=False,
        )
        b.hash_id = gen_random_word(3)
        DBSession.add(b)
        res = b.has_access(user.username)
        self.assertEqual(True, res)
        # Also check if user is None.
        username = None
        res = b.has_access(username)
        self.assertEqual(True, res)

    def test_has_access_diff_user_private(self):
        """Test that a different user cannot view another's private bookmark"""
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        b = Bmark(
            url=gen_random_word(12),
            username=gen_random_word(10),
            is_private=True,
        )
        b.hash_id = gen_random_word(3)
        DBSession.add(b)
        res = b.has_access(user.username)
        self.assertEqual(False, res)
        # Also check if user is None.
        username = None
        res = b.has_access(username)
        self.assertEqual(False, res)

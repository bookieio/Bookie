"""Test the Auth model setup"""
from unittest import TestCase
from nose.tools import ok_, eq_

from bookie.models.auth import User

class TestPassword(TestCase):
    """Test password checks"""
    pass


class TestAuthUser(TestCase):
    """Test User Model"""
    test_hash = '$2a$10$FMFKEYqC7kifFTm05iag7etE17Q0AyKvtX88XUdUcM7rvpz48He92'
    test_password = 'testing'

    def setUp(self):
        """Setup Tests"""
        pass

    def tearDown(self):
        """Tear down each test"""
        pass

    def test_password_set(self):
        """Make sure we get the proper hashed password"""
        tst = User()
        tst.password = self.test_password

        eq_(len(tst.password), 60,
                "Hashed should be 60 char long: " + tst.password)
        eq_('$2a$', tst.password[:4],
                "Hash should start with the right complexity: " + tst.password[:4])

    def test_password_match(self):
        """Try to match a given hash"""

        tst = User()
        tst._password = self.test_hash

        ok_(tst._password == self.test_hash, "Setting should have hash")
        ok_(tst.password == self.test_hash, "Getting should have hash")
        ok_(tst.validate_password(self.test_password),
                "The password should check out against the given hash")

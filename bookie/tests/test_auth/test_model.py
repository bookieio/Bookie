"""Test the Auth model setup"""
import transaction
from unittest import TestCase
from nose.tools import ok_, eq_

from bookie.models import DBSession
from bookie.models.auth import User
from bookie.models.auth import UserMgr

from bookie.tests import empty_db

# class TestPassword(TestCase):
#     """Test password checks"""
#     pass
# 
# 
# class TestAuthUser(TestCase):
#     """Test User Model"""
#     test_hash = '$2a$10$FMFKEYqC7kifFTm05iag7etE17Q0AyKvtX88XUdUcM7rvpz48He92'
#     test_password = 'testing'
# 
#     def test_password_set(self):
#         """Make sure we get the proper hashed password"""
#         tst = User()
#         tst.password = self.test_password
# 
#         eq_(len(tst.password), 60,
#                 "Hashed should be 60 char long: " + tst.password)
#         eq_('$2a$', tst.password[:4],
#                 "Hash should start with the right complexity: " + tst.password[:4])
# 
#     def test_password_match(self):
#         """Try to match a given hash"""
# 
#         tst = User()
#         tst._password = self.test_hash
# 
#         ok_(tst._password == self.test_hash, "Setting should have hash")
#         ok_(tst.password == self.test_hash, "Getting should have hash")
#         ok_(tst.validate_password(self.test_password),
#                 "The password should check out against the given hash: " + tst.password)
# 
# 
# class TestAuthMgr(TestCase):
#     """Test User Manager"""
# 
#     def test_get_id(self):
#         """Fetching user by the id"""
#         # the migration adds an initial admin user to the system
#         user = UserMgr.get(user_id=1)
#         eq_(user.id, 1,
#                 "Should have a user id of 1: " + str(user.id))
#         eq_(user.username, 'admin',
#                 "Should have a username of admin: " + user.username)
# 
#     def test_get_username(self):
#         """Fetching the user by the username"""
#         user = UserMgr.get(username='admin')
#         eq_(user.id, 1,
#                 "Should have a user id of 1: " + str(user.id))
#         eq_(user.username, 'admin',
#                 "Should have a username of admin: " + user.username)
# 
#     def test_get_bad_user(self):
#         """We shouldn't get a hit if the user is inactive"""
#         user = UserMgr.get(username='noexist')
# 
#         eq_(user, None,
#                 "Should not find a non-existant user: " + str(user))

"""Test that we're meeting delicious API specifications"""
from datetime import datetime, timedelta
import logging
import transaction
import unittest
from mock import Mock, patch
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.lib import access
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Tag
from bookie.models import bmarks_tags

LOG = logging.getLogger(__name__)

# class BookieViewsTest(unittest.TestCase):
#     """Test the normal web views user's user"""
# 
#     def _add_bmark(self):
#         # setup the default bookie bookmark
#         import logging
#         log = logging.getLogger(__name__)
#         log.error('called to add bmark')
#         bmark_us = Bmark('http://bmark.us',
#                          username="admin",
#                          desc="Bookie Website",
#                          ext= "Bookie Documentation Home",
#                          tags = "bookmarks")
# 
#         bmark_us.stored = datetime.now()
#         bmark_us.updated = datetime.now()
#         DBSession.add(bmark_us)
#         transaction.commit()
# 
#     def setUp(self):
#         from pyramid.paster import get_app
#         from bookie.tests import BOOKIE_TEST_INI
#         app = get_app(BOOKIE_TEST_INI, 'main')
#         from webtest import TestApp
#         self.testapp = TestApp(app)
#         testing.setUp()
# 
#     def tearDown(self):
#         """We need to empty the bmarks table on each run"""
#         testing.tearDown()
#         session = DBSession()
#         Bmark.query.delete()
#         Tag.query.delete()
#         Hashed.query.delete()
#         session.execute(bmarks_tags.delete())
#         session.flush()
#         transaction.commit()
# 
#     def test_bookmark_recent(self):
#         """Verify we can call the /recent url """
#         self._add_bmark()
#         body_str = "Recent Bookmarks"
# 
#         res = self.testapp.get('/recent')
# 
#         eq_(res.status, "200 OK",
#             msg='recent status is 200, ' + res.status)
#         ok_(body_str in res.body,
#             msg="Request should contain body_str: " + res.body)
# 
#     def test_recent_page(self):
#         """We should be able to page through the list"""
#         body_str = "Prev"
# 
#         res = self.testapp.get('/recent?page=1')
#         eq_(res.status, "200 OK",
#             msg='recent page 1 status is 200, ' + res.status)
#         ok_(body_str in res.body,
#             msg="Page 1 should contain body_str: " + res.body)
# 
#     def test_import_auth_failed(self):
#         """Veryify that without the right API key we get forbidden"""
#         post = {
#             'api_key': 'wrong_key'
#         }
# 
#         res = self.testapp.post('/admin/import', params=post, status=403)
# 
#         eq_(res.status, "403 Forbidden",
#             msg='Import status is 403, ' + res.status)
# 
#     def test_bookmark_tag(self):
#         """Verify we can call the /tags/bookmarks url """
#         self._add_bmark()
# 
#         body_str = "Bookmarks: bookmarks"
#         res = self.testapp.get('/tags/bookmarks')
# 
#         eq_(res.status, "200 OK",
#             msg='recent status is 200, ' + res.status)
#         ok_(body_str in res.body,
#             msg="Request should contain body_str: " + res.body)
# 
#     def test_bookmark_tag_no_edits(self):
#          """Verify the tags view"""
#          self._add_bmark()
# 
#          delete_str = "/bmark/confirm/delete"
#          res = self.testapp.get('/tags/bookmarks')
# 
#          ok_(delete_str not in res.body,
#              msg="Tag view delete link should NOT be visible:" + res.body)

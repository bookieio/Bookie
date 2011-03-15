"""Test that we're meeting delicious API specifications"""
from datetime import datetime, timedelta
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark, NoResultFound
from bookie.models import Tag, bmarks_tags


class BookieViewsTest(unittest.TestCase):
    """Test the normal web views user's user"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini', 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()

    def test_bookmark_recent(self):
        """Verify we can call the /recent url """
        body_str = "Recent Bookmarks"

        res = self.testapp.get('/recent')
        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Request should contain body_str: " + res.body)

    def test_recent_page(self):
        """We should be able to page through the list"""
        body_str = "Prev"

        res = self.testapp.get('/recent/1')
        eq_(res.status, "200 OK",
            msg='recent page 1 status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Page 1 should contain body_str: " + res.body)



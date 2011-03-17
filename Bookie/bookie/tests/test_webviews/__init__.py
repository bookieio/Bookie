"""Test that we're meeting delicious API specifications"""
from datetime import datetime, timedelta
import transaction
import unittest
from mock import Mock
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Tag
from bookie.models import bmarks_tags


class BookieViewsTest(unittest.TestCase):
    """Test the normal web views user's user"""

    def _add_bmark(self):
        # setup the default bookie bookmark
        import logging
        log = logging.getLogger(__name__)
        log.error('called to add bmark')
        bmark_us = Bmark('http://bmark/us',
                         desc="Bookie Website",
                         ext= "Bookie Documentation Home",
                         tags = "bookmarks")

        bmark_us.stored = datetime.now()
        bmark_us.updated = datetime.now()
        DBSession.add(bmark_us)
        transaction.commit()

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('test.ini', 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def test_bookmark_recent(self):
        """Verify we can call the /recent url """
        self._add_bmark()

        body_str = "Recent Bookmarks"
        delete_str = "bmark/confirm/delete"

        res = self.testapp.get('/recent')

        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Request should contain body_str: " + res.body)

        # there should be a delete link for the default bookie bookmark in the
        # body as well
        ok_(delete_str in res.body,
            msg="The delete link should be visible in the body:" + res.body)

    def test_recent_page(self):
        """We should be able to page through the list"""
        body_str = "Prev"

        res = self.testapp.get('/recent/1')
        eq_(res.status, "200 OK",
            msg='recent page 1 status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Page 1 should contain body_str: " + res.body)

    def test_allow_edit_requests(self):
        """Verify that if allow_edit is false we don't get edit/delete links"""
        self._add_bmark()

        from bookie.views import bmarks
        bmarks._is_authed = Mock
        bmarks._is_authed.return_value = False

        delete_str = "bmark/confirm/delete"

        res = self.testapp.get('/recent')

        # the delete link should not render if allow_edits is false
        ok_(delete_str not in res.body,
            msg="The delete link should NOT be visible:" + res.body)

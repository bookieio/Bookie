"""Test that we're meeting delicious API specifications"""
import feedparser
import logging
import time
import transaction
import unittest
from datetime import datetime
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.tests import TestViewBase
from bookie.tests import empty_db
from bookie.tests.factory import make_bookmark

LOG = logging.getLogger(__name__)


class BookieViewsTest(unittest.TestCase):
    """Test the normal web views user's user"""

    def _add_bmark(self):
        # setup the default bookie bookmark
        import logging
        log = logging.getLogger(__name__)
        log.error('called to add bmark')
        bmark_us = Bmark('http://bmark.us',
                         username="admin",
                         desc=u"Bookie Website",
                         ext=u"Bookie Documentation Home",
                         tags=u"bookmarks")

        bmark_us.stored = datetime.now()
        bmark_us.updated = datetime.now()
        transaction.commit()

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        empty_db()

    def test_bookmark_recent(self):
        """Verify we can call the /recent url """
        self._add_bmark()
        body_str = "Recent Bookmarks"

        res = self.testapp.get('/recent')

        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Request should contain body_str: " + res.body)

    def test_recent_page(self):
        """We should be able to page through the list"""
        body_str = "Prev"

        res = self.testapp.get('/recent?page=1')
        eq_(res.status, "200 OK",
            msg='recent page 1 status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Page 1 should contain body_str: " + res.body)

    def test_import_auth_failed(self):
        """Veryify that without the right API key we get forbidden"""
        post = {
            'api_key': 'wrong_key'
        }

        res = self.testapp.post('/admin/import', params=post, status=403)

        eq_(res.status, "403 Forbidden",
            msg='Import status is 403, ' + res.status)


class TestNewBookmark(TestViewBase):
    """Test the new bookmark real views"""

    def test_renders(self):
        """Verify that we can call the /new url"""
        self._login_admin()
        res = self.app.get('/admin/new')
        ok_('Add Bookmark' in res.body,
            "Should see the add bookmark title")


class TestRSSFeeds(TestViewBase):
    """Verify the RSS feeds function correctly."""

    def test_rss_added(self):
        """Viewing /recent should have a rss url in the content."""
        body_str = "application/rss+xml"
        res = self.app.get('/recent')

        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Request should contain rss str: " + res.body)

    def test_rss_matches_request(self):
        """The url should match the /recent request with tags."""
        body_str = "rss/ubuntu"
        res = self.app.get('/recent/ubuntu')

        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)
        ok_(body_str in res.body,
            msg="Request should contain rss url: " + res.body)

    def test_rss_is_parseable(self):
        """The rss feed should be a parseable feed."""
        bmarks = [make_bookmark() for i in range(10)]
        transaction.commit()

        res = self.app.get('/rss')

        eq_(res.status, "200 OK",
            msg='recent status is 200, ' + res.status)

        # http://packages.python.org/feedparser/introduction.html#parsing-a-feed-from-a-string
        parsed = feedparser.parse(res.body)
        links = []
        for entry in parsed.entries:
            links.append({
                'title': entry.title,
                'category': entry.category,
                'date': time.strftime('%d %b %Y', entry.updated_parsed),
                'description': entry.description,
                'link': entry.link,
                })

        ok_(links, 'The feed should have a list of links.')
        eq_(10, len(links), 'There are 10 links in the feed.')

        sample_item = links[0]
        ok_(sample_item['title'], 'Items have a title.')
        ok_(sample_item['link'], 'Items have a link to reach things.')
        ok_(sample_item['description'], 'Items have a description string.')

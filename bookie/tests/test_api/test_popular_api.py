import logging
import json
import transaction
import unittest
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models.auth import User
from bookie.tests import BOOKIE_TEST_INI
from bookie.tests import empty_db
from bookie.tests import gen_random_word
from random import randint

LOG = logging.getLogger(__name__)

API_KEY = None
MAX_CLICKS = 60


class BookiePopularAPITest(unittest.TestCase):
    """Test the Bookie API for retreiving popular bookmarks"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

        global API_KEY
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        API_KEY = res['api_key']

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        empty_db()

    def _check_cors_headers(self, res):
        """ Make sure that the request has proper CORS headers."""
        self.assertEqual(res.headers['access-control-allow-origin'], '*')
        self.assertEqual(
            res.headers['access-control-allow-headers'], 'X-Requested-With')

    def _add_bookmark(self, user=None):
        """Add a bookmark for a particular user
           with random click count.
           If no user is specified, then admin is used
           for the username"""
        if user:
            DBSession.add(user)
            username = user.username
        else:
            username = u'admin'

        b = Bmark(
            url=gen_random_word(12),
            username=username,
            tags=gen_random_word(4),
        )

        b.clicks = randint(0, MAX_CLICKS)
        b.hash_id = gen_random_word(5)

        DBSession.add(b)
        transaction.commit()
        DBSession.flush()

    def test_bookmark_popular_user(self):
        """Test that we can get a list of bookmarks
           added by admin and sorted by popularity."""
        # Populating DB with some bookmarks of random users.
        user_bmark_count = randint(1, 5)
        for i in range(user_bmark_count):
            user = User()
            user.username = gen_random_word(10)
            self._add_bookmark(user)

        admin_bmark_count = randint(1, 5)
        # Populating DB with some bookmarks of admin.
        for i in range(admin_bmark_count):
            self._add_bookmark()

        res = self.testapp.get('/api/v1/admin/bmarks?sort=popular&api_key=' +
                               API_KEY,
                               status=200)

        # make sure we can decode the body
        bmarks = json.loads(res.body)['bmarks']

        self.assertEqual(
            len(bmarks),
            admin_bmark_count,
            "All admin bookmarks are retreived"
        )

        # Initializing number of clicks
        previous_clicks = MAX_CLICKS
        for bmark in bmarks:
            self.assertEqual(
                bmark[u'username'],
                u'admin',
                "Only bookmarks by admin must be displayed")
            self.assertLessEqual(
                bmark[u'clicks'],
                previous_clicks,
                "Current bookmark's clicks must not be greater" +
                "than previous bookmark's clicks")
            previous_clicks = bmark[u'clicks']

        self._check_cors_headers(res)
        empty_db()

    def test_bookmark_popular(self):
        """Test that we can get a list of all bookmarks
           added by random users and sorted by popularity."""
        # Populating DB with some bookmarks of random users.
        user_bmark_count = randint(1, 5)
        for i in range(user_bmark_count):
            user = User()
            user.username = gen_random_word(10)
            self._add_bookmark(user)

        admin_bmark_count = randint(1, 5)
        # Populating DB with some bookmarks of admin.
        for i in range(admin_bmark_count):
            self._add_bookmark()

        res = self.testapp.get('/api/v1/bmarks?sort=popular&api_key='
                               + API_KEY,
                               status=200)

        # make sure we can decode the body
        bmarks = json.loads(res.body)['bmarks']

        self.assertEqual(
            len(bmarks),
            admin_bmark_count + user_bmark_count,
            "All bookmarks are retreived"
        )

        # Initializing number of clicks
        previous_clicks = MAX_CLICKS
        for bmark in bmarks:
            self.assertLessEqual(
                bmark[u'clicks'],
                previous_clicks,
                "Current bookmark's clicks must not be greater" +
                "than previous bookmark's clicks")
            previous_clicks = bmark[u'clicks']

        self._check_cors_headers(res)
        empty_db()

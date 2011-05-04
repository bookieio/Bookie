"""Test the fulltext implementation"""
import transaction
import urllib

from nose.tools import ok_
from pyramid import testing
from unittest import TestCase

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Tag
from bookie.models import bmarks_tags
from bookie.models.fulltext import get_fulltext_handler
from bookie.models.fulltext import SqliteFulltext

class TestFulltext(TestCase):
    """Test that our fulltext classes function"""

    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        session = DBSession()
        Bmark.query.delete()
        Tag.query.delete()
        Hashed.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def _get_good_request(self, new_tags=None):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': u'testapi',
        }

        if new_tags:
            prms['tags'] = new_tags

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)
        session.flush()
        transaction.commit()
        return res

    def test_get_handler(self):
        """Verify we get the right type of full text store object"""
        sqlite_str = "sqlite:///somedb.db"

        handler = get_fulltext_handler(sqlite_str)

        ok_(isinstance(handler, SqliteFulltext),
                "Should get a sqlite fulltext handler")

    def test_sqlite_save(self):
        """Verify that if we store a bookmark we get the fulltext storage"""
        # first let's add a bookmark we can search on
        res = self._get_good_request()

        search_res = self.testapp.get('/search?search=google')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('my google desc' in search_res.body,
            "We should find our description on the page: " + search_res.body)

        search_res = self.testapp.get('/search?search=python')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('my google desc' in search_res.body,
            "Tag search should find our description on the page: " + search_res.body)

        search_res = self.testapp.get('/search?search=extended%20notes')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('extended notes' in search_res.body,
            "Extended search should find our description on the page: " + search_res.body)

    def test_sqlite_update(self):
        """Verify that if we update a bookmark, fulltext is updated

        We need to make sure that updates to the record get cascaded into the
        fulltext table indexes

        """
        self._get_good_request()

        # now we need to do another request with updated tag string
        self._get_good_request(new_tags="google books icons")

        search_res = self.testapp.get('/search?search=icon')
        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('icon' in search_res.body,
            "We should find the new tag icon on the page: " + search_res.body)

    def test_restlike_search(self):
        """Verify that our searches work with the more restful like url match"""
        # first let's add a bookmark we can search on
        self._get_good_request()

        search_res = self.testapp.get('/search/google')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('my google desc' in search_res.body,
            "We should find our description on the page: " + search_res.body)

        search_res = self.testapp.get('/search/python')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('my google desc' in search_res.body,
            "Tag search should find our description on the page: " + search_res.body)

        search_res = self.testapp.get('/search/extended/notes')

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('extended notes' in search_res.body,
            "Extended search should find our description on the page: " + search_res.body)

    def test_ajax_search(self):
        """Verify that we can get a json MorJSON response when ajax search"""
        # first let's add a bookmark we can search on
        self._get_good_request()

        search_res = self.testapp.get(
                        '/search/google',
                        headers = {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json'
                        }
        )

        ok_(search_res.status == '200 OK',
                "Status is 200: " + search_res.status)

        ok_('my google desc' in search_res.body,
            "We should find our description on the page: " + search_res.body)

        # also check for our specific json bits
        ok_('success' in search_res.body,
                "We should see a success bit in the json: " + search_res.body)

        ok_('payload' in search_res.body,
                "We should see a payload bit in the json: " + search_res.body)

        ok_('message' in search_res.body,
                "We should see a message bit in the json: " + search_res.body)


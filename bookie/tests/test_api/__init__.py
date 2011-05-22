"""Test that we're meeting delicious API specifications"""
import logging
import json
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.tests import BOOKIE_TEST_INI
from bookie.tests import empty_db

GOOGLE_HASH = 'aa2239c17609'
LOG = logging.getLogger(__name__)

class BookieAPITest(unittest.TestCase):
    """Test the Bookie API"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        empty_db()

    def _get_good_request(self, content=False, second_bmark=False):
        """Return the basics for a good add bookmark request"""
        session = DBSession()

        if second_bmark:
            prms = {
                    'url': u'http://bmark.us',
                    'description': u'Bookie',
                    'extended': u'Extended notes',
                    'tags': u'bookmarks',
                    'api_key': u'testapi',
            }

            # if we want to test the readable fulltext side we want to make sure we
            # pass content into the new bookmark
            prms['content'] = "<h1>Second bookmark man</h1>"

            req_params = urllib.urlencode(prms)
            res = self.testapp.get('/delapi/posts/add?' + req_params)

        # the main bookmark, added second to prove popular will sort correctly
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': u'testapi',
        }

        # if we want to test the readable fulltext side we want to make sure we
        # pass content into the new bookmark
        if content:
            prms['content'] = "<h1>There's some content in here dude</h1>"

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/delapi/posts/add?' + req_params)

        session.flush()
        transaction.commit()
        return res

    def test_bookmark_fetch(self):
        """Test that we can get a bookmark and it's details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/bmarks/' + GOOGLE_HASH)

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmark = json.loads(res.body)['payload']['bmark']
        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        ok_(u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        ok_(bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" + str(bmark[u'tags'][0][u'name']))

        ok_(u'readable' in bmark,
            "We should have readable content")

        ok_('dude' in bmark['readable']['content'],
                "We should have 'dude' in our content: " + bmark['readable']['content'])

    def test_bookmark_recent(self):
        """Test that we can get list of bookmarks with details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/bmarks/recent')

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmark = json.loads(res.body)['payload']['bmarks'][0]
        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        ok_(u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        ok_(bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" + str(bmark[u'tags'][0][u'name']))

    def test_bookmark_popular(self):
        """Test that we can get list of bookmarks with details"""
        self._get_good_request(content=True, second_bmark=True)

        # we want to make sure the click count of 0 is greater than 1
        res = self.testapp.get('/redirect/' + GOOGLE_HASH)
        res = self.testapp.get('/redirect/' + GOOGLE_HASH)

        res = self.testapp.get('/api/v1/bmarks/popular')

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmark_list = json.loads(res.body)['payload']['bmarks']

        eq_(len(bmark_list), 2,
                "We should have two results coming back")

        bmark1 = bmark_list[0]
        bmark2 = bmark_list[1]

        eq_(GOOGLE_HASH, bmark1[u'hash_id'],
            "The hash_id should match: " + str(bmark1[u'hash_id']))

        ok_('clicks' in bmark1,
            "The clicks field should be in there")
        eq_(2, bmark1['clicks'],
            "The clicks should be 2: " + str(bmark1['clicks']))
        eq_(0, bmark2['clicks'],
            "The clicks should be 0: " + str(bmark2['clicks']))

    def test_paging_results(self):
        """Test that we can page results"""
        self._get_good_request(content=True, second_bmark=True)

        # test that we only get one resultback
        res = self.testapp.get('/api/v1/bmarks/recent?page=0&count=1')

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmarks = json.loads(res.body)['payload']['bmarks']

        eq_(len(bmarks), 1, "We should only have one result in this page")

        res = self.testapp.get('/api/v1/bmarks/recent?page=1&count=1')

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmarks = json.loads(res.body)['payload']['bmarks']

        eq_(len(bmarks), 1,
            "We should only have one result in the second page")

        res = self.testapp.get('/api/v1/bmarks/recent?page=2&count=1')

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        # make sure we can decode the body
        bmarks = json.loads(res.body)['payload']['bmarks']

        eq_(len(bmarks), 0,
            "We should not have any results for page 2")

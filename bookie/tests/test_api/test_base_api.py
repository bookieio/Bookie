"""Test that we're meeting delicious API specifications"""
# Need to create a new renderer that wraps the jsonp renderer and adds these
# heads to all responses. Then the api needs to be adjusted to use this new
# renderer type vs jsonp.
import json
import logging
import os
import transaction
import unittest
from pyramid import testing

from bookie.models import (
    BmarkMgr,
    DBSession,
    Readable,
)
from bookie.models.auth import Activation
from bookie.tests import BOOKIE_TEST_INI
from bookie.tests import empty_db
from bookie.tests import factory
from bookie.tests import gen_random_word
from bookie.tests.factory import make_bookmark

from datetime import datetime


GOOGLE_HASH = u'aa2239c17609b2'
BMARKUS_HASH = u'c5c21717c99797'
LOG = logging.getLogger(__name__)

API_KEY = None


class BookieAPITest(unittest.TestCase):
    """Test the Bookie API"""

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

    def _get_good_request(self, content=False, second_bmark=False,
                          is_private=False, username=None, api_key=None,
                          url=None):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        if not username:
            username = u'admin'
        if not api_key:
            api_key = API_KEY
        if not url:
            url = u'http://google.com'

        # the main bookmark, added second to prove popular will sort correctly
        prms = {
            'url': url,
            'description': u'This is my google desc',
            'extended': u'And some extended notes about it in full form',
            'tags': u'python search',
            'api_key': api_key,
            'username': username,
            'inserted_by': u'chrome_ext',
            'is_private': is_private,
        }

        # if we want to test the readable fulltext side we want to make sure we
        # pass content into the new bookmark
        if content:
            prms['content'] = u"<p>There's some content in here dude</p>"

        # rself.assertEqualparams = urllib.urlencode(prms)
        res = self.testapp.post(
            '/api/v1/{0}/bmark?'.format(username),
            content_type='application/json',
            params=json.dumps(prms),
        )

        if second_bmark:
            prms = {
                'url': u'http://bmark.us',
                'description': u'Bookie',
                'extended': u'Exteded notes',
                'tags': u'bookmarks',
                'api_key': API_KEY,
                'username': u'admin',
                'inserted_by': u'chrome_ext',
            }

            # if we want to test the readable fulltext side we want to make
            # sure we pass content into the new bookmark
            prms['content'] = u"<h1>Second bookmark man</h1>"

            # rself.assertEqualparams = urllib.urlencode(prms)
            res = self.testapp.post(
                '/api/v1/admin/bmark?',
                content_type='application/json',
                params=json.dumps(prms)
            )

        session.flush()
        transaction.commit()
        # Run the celery task for indexing this bookmark.
        from bookie.bcelery import tasks
        tasks.reindex_fulltext_allbookmarks(sync=True)
        return res

    def _setup_user_bookmark_count(self):
        """Fake user bookmark counts are inserted into the database"""
        test_date_1 = datetime(2013, 11, 25)
        stat1 = factory.make_user_bookmark_count(username=u'admin',
                                                 data=20,
                                                 tstamp=test_date_1)
        test_date_2 = datetime(2013, 11, 15)
        stat2 = factory.make_user_bookmark_count(username=u'admin',
                                                 data=30,
                                                 tstamp=test_date_2)
        test_date_3 = datetime(2013, 12, 28)
        stat3 = factory.make_user_bookmark_count(username=u'admin',
                                                 data=15,
                                                 tstamp=test_date_3)
        transaction.commit()
        return [stat1, stat2, stat3]

    def _make_test_bookmarks(self):
        """Create a new test user and bookmarks by admin and test user"""
        # Make a test user.
        test_user_username = u'test_user'
        test_user = factory.make_user(username=test_user_username)
        test_user.api_key = u'random_key'
        transaction.commit()
        test_user = DBSession.merge(test_user)

        bmark_test = {}
        bmark_test['admin_public_bmark'] = {
            'url': u'http://google1.com',
            'username': u'admin',
            'api_key': API_KEY,
            'is_private': False,
        }
        bmark_test['admin_private_bmark'] = {
            'url': u'http://google2.com',
            'username': u'admin',
            'api_key': API_KEY,
            'is_private': True,
        }
        bmark_test['user_public_bmark'] = {
            'url': u'http://google3.com',
            'username': test_user.username,
            'api_key': test_user.api_key,
            'is_private': False,
        }
        bmark_test['user_private_bmark'] = {
            'url': u'http://google4.com',
            'username': test_user.username,
            'api_key': test_user.api_key,
            'is_private': True,
        }

        # Make the bookmarks.
        for bmark in bmark_test.keys():
            self._get_good_request(url=bmark_test[bmark]['url'],
                                   username=bmark_test[bmark]['username'],
                                   api_key=bmark_test[bmark]['api_key'],
                                   is_private=bmark_test[bmark]['is_private'])

        return (test_user, bmark_test)

    def test_add_bookmark(self):
        """We should be able to add a new public bookmark to the system"""
        # we need to know what the current admin's api key is so we can try to
        # add
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']

        test_bmark = {
            'url': u'http://bmark.us',
            'description': u'Bookie',
            'extended': u'Extended notes',
            'tags': u'bookmarks',
            'api_key': key,
            'username': u'admin',
            'is_private': False,
        }

        res = self.testapp.post('/api/v1/admin/bmark',
                                content_type='application/json',
                                params=json.dumps(test_bmark),
                                status=200)

        self.assertTrue(
            '"location":' in res.body,
            "Should have a location result: " + res.body)
        self.assertTrue(
            'description": "Bookie"' in res.body,
            "Should have Bookie in description: " + res.body)
        self.assertTrue(
            '"is_private": false' in res.body,
            "Should have is_private as false: " + res.body)
        self._check_cors_headers(res)

    def test_add_private_bookmark(self):
        """We should be able to add a new private bookmark to the system"""
        # we need to know what the current admin's api key is so we can try to
        # add
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']

        test_bmark = {
            'url': u'http://bmark.us',
            'description': u'Bookie',
            'extended': u'Extended notes',
            'tags': u'bookmarks',
            'api_key': key,
            'username': u'admin',
            'is_private': 'true',
        }

        res = self.testapp.post('/api/v1/admin/bmark',
                                content_type='application/json',
                                params=json.dumps(test_bmark),
                                status=200)

        self.assertTrue(
            '"location":' in res.body,
            "Should have a location result: " + res.body)
        self.assertTrue(
            'description": "Bookie"' in res.body,
            "Should have Bookie in description: " + res.body)
        self.assertTrue(
            '"is_private": true' in res.body,
            "Should have is_private as true: " + res.body)
        self._check_cors_headers(res)

    def test_add_bookmark_empty_body(self):
        """When missing a POST body we get an error response."""
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']

        res = self.testapp.post(
            str('/api/v1/admin/bmark?api_key={0}'.format(key)),
            params={},
            status=400)

        data = json.loads(res.body)
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Bad Request: No url provided')

    def test_add_bookmark_missing_url_in_JSON(self):
        """When missing the url in the JSON POST we get an error response."""
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']

        params = {
            'description': u'This is my test desc',
        }

        res = self.testapp.post(
            str('/api/v1/admin/bmark?api_key={0}'.format(key)),
            content_type='application/json',
            params=json.dumps(params),
            status=400)

        data = json.loads(res.body)
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Bad Request: No url provided')

    def test_bookmark_fetch(self):
        """Test that we can get a bookmark and it's details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/admin/bmark/{0}?api_key={1}'.format(
                               GOOGLE_HASH,
                               API_KEY),
                               status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmark']
        self.assertEqual(
            GOOGLE_HASH,
            bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        self.assertTrue(
            u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        self.assertTrue(
            bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" +
            str(bmark[u'tags'][0][u'name']))

        self.assertTrue(
            u'readable' not in bmark,
            "We should not have readable content")

        self.assertEqual(
            u'python search', bmark[u'tag_str'],
            "tag_str should be populated: " + str(dict(bmark)))

        # to get readble content we need to pass the flash with_content
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}&with_content=true'.format(
                GOOGLE_HASH,
                API_KEY),
            status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmark']

        self.assertTrue(
            u'readable' in bmark,
            "We should have readable content")

        self.assertTrue(
            'dude' in bmark['readable']['content'],
            "We should have 'dude' in our content: " +
            bmark['readable']['content'])
        self._check_cors_headers(res)

    def test_bookmark_fetch_with_suggestions(self):
        """When a very recent bookmark is present return it."""
        self._get_good_request(content=True, second_bmark=True)
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}'.format(GOOGLE_HASH),
            {
                'api_key': API_KEY,
                'url': 'http://google.com',
                'description': 'The best search engine for Python things.'
            },
            status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)
        self.assertIn('tag_suggestions', bmark)
        self.assertIn('search', bmark['tag_suggestions'])
        self._check_cors_headers(res)

    def test_no_bookmark_fetch_with_suggestions(self):
        """When a very recent bookmark is present return it."""
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}'.format(GOOGLE_HASH),
            {
                'api_key': API_KEY,
                'url': 'http://google.com',
                'description': 'The best search engine for Python things.'
            },
            status=404)

        # make sure we can decode the body
        bmark = json.loads(res.body)
        self.assertIn('tag_suggestions', bmark)
        self.assertIn('search', bmark['tag_suggestions'])
        self._check_cors_headers(res)

    def test_suggested_tags(self):
        """Suggestions based on the content of the bookmarked page"""
        # login into bookie
        user_data = {'login': u'admin',
                     'password': u'admin',
                     'form.submitted': u'true'}
        res = self.testapp.post('/login',
                                params=user_data)
        # Add a bookmark
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']
        url = u'http://testing_tags.com'
        # set the readable content for the bookmark
        path = os.getcwd()+"/bookie/tests/test_api/tag_test.txt"
        content = open(path, 'r').read()
        test_bmark = {
            'url': url,
            'description': u'Bookie',
            'extended': u'',
            'tags': u'',
            'api_key': key,
            'content': content,
        }
        res = self.testapp.post('/api/v1/admin/bmark',
                                params=test_bmark,
                                status=200)

        bmark = BmarkMgr.get_by_url(url)
        hash_id = bmark.hash_id
        tags_expected = ['network', 'new', 'simulator', 'user']
        edit_bmark = {
            'hash_id': hash_id,
            'username': 'admin',
            'url': url
        }
        hash_id = str(hash_id)
        res = self.testapp.post('/admin/edit/' + hash_id,
                                params=edit_bmark,
                                status=200)
        # pure numbers are eliminated
        self.assertNotIn('2014', res.body)
        # tags with length less than 3 are omitted
        self.assertNotIn('NS', res.body)
        # all tags are lower cased
        self.assertNotIn('NEW', res.body)
        for tag in tags_expected:
            self.assertIn(tag, res.body)

    def test_suggested_tags_for_unparsed_bookmark(self):
        """Suggested tags for a bookmarked page whose readable is None"""
        # Login into bookie
        user_data = {'login': u'admin',
                     'password': u'admin',
                     'form.submitted': u'true'}
        self.testapp.post('/login',
                          params=user_data)
        # Add a bookmark
        test_bmark = make_bookmark()
        test_bmark.url = u'http://testing_tags.com'
        test_bmark.description = u'Bookie'
        path = os.getcwd() + "/bookie/tests/test_api/tag_test.txt"
        content = open(path, 'r').read()
        test_bmark.readable = Readable(content=content)

        # Add another bookmark with readable as None
        new_url = u'http://testing_readable_none.com'
        no_readable_bmark = make_bookmark()
        no_readable_bmark.url = new_url
        no_readable_bmark.description = u'Readable of this bookmark is None'

        DBSession.add(test_bmark)
        DBSession.add(no_readable_bmark)
        DBSession.flush()
        no_readable_hash = no_readable_bmark.hash_id

        transaction.commit()

        edit_bmark = {
            'hash_id': no_readable_hash,
            'username': 'admin',
        }

        # As the Bookmark's readable is None the page should load without
        # error.
        self.testapp.post(
            u'/admin/edit/' + no_readable_hash,
            params=edit_bmark,
            status=200)

    def test_bookmark_fetch_fail(self):
        """Verify we get a failed response when wrong bookmark"""
        self._get_good_request()

        # test that we get a 404
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(BMARKUS_HASH,
                                                         API_KEY),
            status=404)
        self._check_cors_headers(res)

    def test_bookmark_diff_user(self):
        """Verify that anon users can access the public bookmark"""
        self._get_good_request()

        # test that we get a 200
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}'.format(GOOGLE_HASH),
            status=200)
        self._check_cors_headers(res)

    def test_no_access_to_private_bookmark(self):
        """Verify that anon users cannot access the private bookmark"""
        self._get_good_request(is_private=True)

        # test that we get a 404
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}'.format(GOOGLE_HASH),
            status=404)
        self._check_cors_headers(res)

    def test_bookmark_diff_user_authed(self):
        """Verify an auth'd user can fetch another's public bookmark"""
        self._get_good_request()

        # test that we get a 200
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(GOOGLE_HASH,
                                                         'invalid'),
            status=200)
        self._check_cors_headers(res)

    def test_bookmark_diff_user_authed_accounts_for_privacy(self):
        """Verify an auth'd user cannot fetch another's private bookmark"""
        self._get_good_request(is_private=True)

        # test that we get a 404
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(GOOGLE_HASH,
                                                         'invalid'),
            status=404)
        self._check_cors_headers(res)

    def test_bookmark_same_user_authed(self):
        """Verify an auth'd user can fetch their public bookmark"""
        self._get_good_request()

        # test that we get a 200
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(GOOGLE_HASH, API_KEY),
            status=200)
        self._check_cors_headers(res)

    def test_bookmark_same_user_authed_accounts_for_privacy(self):
        """Verify an auth'd user can fetch their private bookmark"""
        self._get_good_request(is_private=True)

        # test that we get a 200
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(GOOGLE_HASH, API_KEY),
            status=200)
        self._check_cors_headers(res)

    def test_bookmark_remove(self):
        """A delete call should remove the bookmark from the system"""
        self._get_good_request(content=True, second_bmark=True)

        # now let's delete the google bookmark
        res = self.testapp.delete(
            '/api/v1/admin/bmark/{0}?api_key={1}'.format(
                GOOGLE_HASH,
                API_KEY),
            status=200)

        self.assertTrue(
            'message": "done"' in res.body,
            "Should have a message of done: " + res.body)

        # we're going to cheat like mad, use the sync call to get the hash_ids
        # of bookmarks in the system and verify that only the bmark.us hash_id
        # is in the response body
        res = self.testapp.get('/api/v1/admin/extension/sync',
                               params={'api_key': API_KEY},
                               status=200)

        self.assertTrue(
            GOOGLE_HASH not in res.body,
            "Should not have the google hash: " + res.body)
        self.assertTrue(
            BMARKUS_HASH in res.body,
            "Should have the bmark.us hash: " + res.body)
        self._check_cors_headers(res)

    def test_bookmark_recent_same_user(self):
        """Test that we can get list of all bookmarks with details"""
        self._get_good_request(content=True, second_bmark=True)
        res = self.testapp.get('/api/v1/admin/bmarks?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        first_bmark = json.loads(res.body)['bmarks'][0]
        second_bmark = json.loads(res.body)['bmarks'][1]
        self.assertEqual(
            BMARKUS_HASH,
            first_bmark[u'hash_id'],
            "The hash_id should match: " + str(first_bmark[u'hash_id']))

        self.assertTrue(
            u'tags' in first_bmark,
            "We should have a list of tags in the bmark returned")

        self.assertEqual(
            u'bookmarks',
            first_bmark[u'tags'][0][u'name'],
            "Tag should be bookmarks: " +
            str(first_bmark[u'tags'][0][u'name']))

        self.assertEqual(
            GOOGLE_HASH,
            second_bmark[u'hash_id'],
            "The hash_id should match: " + str(second_bmark[u'hash_id']))

        self.assertTrue(
            u'tags' in second_bmark,
            "We should have a list of tags in the bmark returned")

        self.assertTrue(
            second_bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" +
            str(second_bmark[u'tags'][0][u'name']))

        res = self.testapp.get(
            '/api/v1/admin/bmarks?with_content=true&api_key=' + API_KEY,
            status=200)
        self._check_cors_headers(res)

        # make sure we can decode the body
        # @todo this is out because of the issue noted in the code. We'll
        # clean this up at some point.
        # bmark = json.loads(res.body)['bmarks'][0]
        # self.assertTrue('here dude' in bmark[u'readable']['content'],
        #     "There should be content: " + str(bmark))

    def test_bookmark_recent_diff_user(self):
        """Test that we can get a list of only public bookmarks with details"""
        self._get_good_request(content=True, second_bmark=True)
        diff_user_api_key = gen_random_word(6)
        res = self.testapp.get('/api/v1/admin/bmarks?api_key=' +
                               diff_user_api_key,
                               status=200)

        # Make sure we can decode the body.
        bmark = json.loads(res.body)['bmarks'][1]
        self.assertEqual(
            GOOGLE_HASH,
            bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        self.assertTrue(
            u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        self.assertTrue(
            bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search: " +
            str(bmark[u'tags'][0][u'name']))

        res = self.testapp.get(
            '/api/v1/admin/bmarks?with_content=true&api_key=' +
            diff_user_api_key,
            status=200)
        self._check_cors_headers(res)

    def test_bookmark_recent(self):
        """Test that we can get list of bookmarks with details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/bmarks?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmarks'][0]
        self.assertEqual(
            GOOGLE_HASH,
            bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        self.assertTrue(
            u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        self.assertTrue(
            bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" +
            str(bmark[u'tags'][0][u'name']))

        res = self.testapp.get(
            '/api/v1/admin/bmarks?with_content=true&api_key=' + API_KEY,
            status=200)
        self._check_cors_headers(res)

        # make sure we can decode the body
        # @todo this is out because of the issue noted in the code. We'll
        # clean this up at some point.
        # bmark = json.loads(res.body)['bmarks'][0]
        # self.assertTrue('here dude' in bmark[u'readable']['content'],
        #     "There should be content: " + str(bmark))

    def test_bookmark_sync(self):
        """Test that we can get the sync list from the server"""
        self._get_good_request(content=True, second_bmark=True)

        # test that we only get one resultback
        res = self.testapp.get('/api/v1/admin/extension/sync',
                               params={'api_key': API_KEY},
                               status=200)

        self.assertEqual(
            res.status, "200 OK",
            msg='Get status is 200, ' + res.status)

        self.assertTrue(
            GOOGLE_HASH in res.body,
            "The google hash id should be in the json: " + res.body)
        self.assertTrue(
            BMARKUS_HASH in res.body,
            "The bmark.us hash id should be in the json: " + res.body)
        self._check_cors_headers(res)

    def test_search_api(self):
        """Test that we can get list of bookmarks ordered by clicks"""
        self._get_good_request(content=True, second_bmark=True)

        res = self.testapp.get('/api/v1/bmarks/search/google', status=200)

        # make sure we can decode the body
        bmark_list = json.loads(res.body)
        results = bmark_list['search_results']
        self.assertEqual(
            len(results),
            1,
            "We should have one result coming back: {0}".format(len(results)))

        bmark = results[0]

        self.assertEqual(
            GOOGLE_HASH,
            bmark[u'hash_id'],
            "The hash_id {0} should match: {1} ".format(
                str(GOOGLE_HASH),
                str(bmark[u'hash_id'])))

        self.assertTrue(
            'clicks' in bmark,
            "The clicks field should be in there")
        self._check_cors_headers(res)

    def test_search_api_same_user(self):
        """Test that when username and requested_by are same, the user
        gets back their own bookmarks and other's public bookmarks"""
        test_user, bmark_test = self._make_test_bookmarks()

        expected_res = [bmark_test['admin_public_bmark'],
                        bmark_test['admin_private_bmark'],
                        bmark_test['user_public_bmark']]

        # Search for bookmarks.
        res = self.testapp.get(
            '/api/v1/admin/bmarks/search/google',
            params={'api_key': API_KEY},
            status=200
        )

        # Make sure we can decode the body.
        bmark_list = json.loads(res.body)
        results = bmark_list['search_results']
        self.assertEqual(
            len(results),
            3,
            "We should have three results coming back: {0}".
            format(len(results)))
        for bmark in range(len(results)):
            self.assertTrue(
                results[bmark][u'username'] == expected_res[bmark]['username']
                and results[bmark][u'is_private'] ==
                expected_res[bmark]['is_private'] and
                results[bmark][u'url'] == expected_res[bmark]['url'],
                "We should have a bookmark from {0}".
                format(expected_res[bmark]['username']))
        self._check_cors_headers(res)

    def test_search_api_diff_user(self):
        """Test that when a user requests for other's bookmarks,
        they get only the public ones"""
        test_user, bmark_test = self._make_test_bookmarks()

        expected_res = [bmark_test['admin_public_bmark']]

        # Search for bookmarks.
        res = self.testapp.get(
            '/api/v1/admin/bmarks/search/google',
            status=200
        )

        # Make sure we can decode the body.
        bmark_list = json.loads(res.body)
        results = bmark_list['search_results']
        self.assertEqual(
            len(results),
            1,
            "We should have one result coming back: {0}".
            format(len(results)))
        for bmark in range(len(results)):
            self.assertTrue(
                results[bmark][u'username'] == expected_res[bmark]['username']
                and results[bmark][u'is_private'] ==
                expected_res[bmark]['is_private'] and
                results[bmark][u'url'] == expected_res[bmark]['url'],
                "We should have a bookmark from {0}".
                format(expected_res[bmark]['username']))
        self._check_cors_headers(res)

    def test_search_api_anon_user(self):
        """Test that an anonymous user gets only public bookmarks"""
        test_user, bmark_test = self._make_test_bookmarks()

        expected_res = [bmark_test['admin_public_bmark'],
                        bmark_test['user_public_bmark']]

        # Search for bookmarks.
        res = self.testapp.get(
            '/api/v1/bmarks/search/google',
            status=200
        )

        # Make sure we can decode the body.
        bmark_list = json.loads(res.body)
        results = bmark_list['search_results']
        self.assertEqual(
            len(results),
            2,
            "We should have two results coming back: {0}".
            format(len(results)))
        for bmark in range(len(results)):
            self.assertTrue(
                results[bmark][u'username'] == expected_res[bmark]['username']
                and results[bmark][u'is_private'] ==
                expected_res[bmark]['is_private'] and
                results[bmark][u'url'] == expected_res[bmark]['url'],
                "We should have a bookmark from {0}".
                format(expected_res[bmark]['username']))
        self._check_cors_headers(res)

    def test_search_api_fail(self):
        """Test that request to an out of bound page returns error message"""
        self._get_good_request(content=True, second_bmark=False)

        res = self.testapp.get(
            '/api/v1/bmarks/search/google?page=10',
            status=404
        )
        # make sure we can decode the body
        bmark_list = json.loads(res.body)

        self.assertTrue(
            'error' in bmark_list,
            "The error field should be in there")
        self.assertEqual(
            bmark_list['error'],
            "Bad Request: Page number out of bound",
            "We should have the error message: {0}".format(bmark_list['error'])
        )

        self._check_cors_headers(res)

    def test_bookmark_tag_complete_same_user(self):
        """Test we can complete tags in the system

        By default we should have tags for python, search, bookmarks

        """
        self._get_good_request(second_bmark=True)

        res = self.testapp.get(
            '/api/v1/admin/tags/complete',
            params={
                'tag': 'py',
                'api_key': API_KEY},
            status=200)

        self.assertTrue(
            'python' in res.body,
            "Should have python as a tag completion: " + res.body)

        # we shouldn't get python as an option if we supply bookmarks as the
        # current tag. No bookmarks have both bookmarks & python as tags
        res = self.testapp.get(
            '/api/v1/admin/tags/complete',
            params={
                'tag': u'py',
                'current': u'bookmarks',
                'api_key': API_KEY
            },
            status=200)

        self.assertTrue(
            'python' not in res.body,
            "Should not have python as a tag completion: " + res.body)
        self._check_cors_headers(res)

    def test_bookmark_tag_complete_same_user_accounts_for_privacy(self):
        """Test that same user gets back tag completion from their
        private bookmarks"""
        self._get_good_request(is_private=True)

        res = self.testapp.get(
            '/api/v1/admin/tags/complete',
            params={
                'tag': 'py',
                'api_key': API_KEY},
            status=200)

        self.assertTrue(
            'python' in res.body,
            "Should have python as a tag completion: " + res.body)
        self._check_cors_headers(res)

    def test_bookmark_tag_complete_anon_user(self):
        """Test that anon user gets back tag completion from others
        public bookmarks"""
        self._get_good_request()

        res = self.testapp.get(
            '/api/v1/tags/complete',
            params={
                'tag': 'py'
            },
            status=200)

        self.assertTrue(
            'python' in res.body,
            "Should have python as a tag completion: " + res.body)
        self._check_cors_headers(res)

    def test_bookmark_tag_complete_anon_user_accounts_for_privacy(self):
        """Test that anon user does not get back tag completion from others
        private bookmarks"""
        self._get_good_request(is_private=True)

        res = self.testapp.get(
            '/api/v1/tags/complete',
            params={
                'tag': 'py'
            },
            status=200)

        self.assertTrue(
            'python' not in res.body,
            "Should not have python as a tag completion: " + res.body)
        self._check_cors_headers(res)

    def test_bookmark_tag_complete_unauthorized_access(self):
        self._get_good_request()

        self.testapp.get(
            '/api/v1/admin/tags/complete',
            params={
                'tag': 'py'
            },
            status=403)

    def test_start_defined_end(self):
        """Test getting a user's bookmark count over a period of time when
        only start_date is defined and end_date is None"""
        test_dates = self._setup_user_bookmark_count()
        res = self.testapp.get(u'/api/v1/admin/stats/bmarkcount',
                               params={u'api_key': API_KEY,
                                       u'start_date': u'2013-11-16'},
                               status=200)
        data = json.loads(res.body)
        count = data['count'][0]
        self.assertEqual(
            count['attrib'], test_dates[0][0])
        self.assertEqual(
            count['data'], test_dates[0][1])
        self.assertEqual(
            count['tstamp'], str(test_dates[0][2]))
        # Test start_date and end_date.
        self.assertEqual(
            data['start_date'], u'2013-11-16 00:00:00')
        self.assertEqual(
            data['end_date'], u'2013-12-16 00:00:00')

    def test_start_defined_end_defined(self):
        """Test getting a user's bookmark count over a period of time when both
        start_date and end_date are defined"""
        test_dates = self._setup_user_bookmark_count()
        res = self.testapp.get(u'/api/v1/admin/stats/bmarkcount',
                               params={u'api_key': API_KEY,
                                       u'start_date': u'2013-11-14',
                                       u'end_date': u'2013-11-16'},
                               status=200)
        data = json.loads(res.body)
        count = data['count'][0]
        self.assertEqual(
            count['attrib'], test_dates[1][0])
        self.assertEqual(
            count['data'], test_dates[1][1])
        self.assertEqual(
            count['tstamp'], str(test_dates[1][2]))
        # Test start_date and end_date.
        self.assertEqual(
            data['start_date'], u'2013-11-14 00:00:00')
        self.assertEqual(
            data['end_date'], u'2013-11-16 00:00:00')

    def test_start_end_defined(self):
        """Test getting a user's bookmark count over a period of time when
        start_date is None and end_date is defined"""
        test_dates = self._setup_user_bookmark_count()
        res = self.testapp.get(u'/api/v1/admin/stats/bmarkcount',
                               params={u'api_key': API_KEY,
                                       u'end_date': u'2013-12-29'},
                               status=200)
        data = json.loads(res.body)
        count = data['count'][0]
        self.assertEqual(
            count['attrib'], test_dates[2][0])
        self.assertEqual(
            count['data'], test_dates[2][1])
        self.assertEqual(
            count['tstamp'], str(test_dates[2][2]))
        # Test start_date and end_date.
        self.assertEqual(
            data['start_date'], u'2013-11-29 00:00:00')
        self.assertEqual(
            data['end_date'], u'2013-12-29 00:00:00')

    def test_start_of_month(self):
        """Test getting a user's bookmark count when start_date is the
        first day of the month"""
        test_dates = self._setup_user_bookmark_count()
        res = self.testapp.get(u'/api/v1/admin/stats/bmarkcount',
                               params={u'api_key': API_KEY,
                                       u'start_date': u'2013-11-1'},
                               status=200)
        data = json.loads(res.body)
        count = data['count']
        self.assertEqual(
            count[0]['attrib'], test_dates[1][0])
        self.assertEqual(
            count[0]['data'], test_dates[1][1])
        self.assertEqual(
            count[0]['tstamp'], str(test_dates[1][2]))
        self.assertEqual(
            count[1]['attrib'], test_dates[0][0])
        self.assertEqual(
            count[1]['data'], test_dates[0][1])
        self.assertEqual(
            count[1]['tstamp'], str(test_dates[0][2]))
        # Test start_date and end_date.
        self.assertEqual(
            data['start_date'], u'2013-11-01 00:00:00')
        self.assertEqual(
            data['end_date'], u'2013-11-30 00:00:00')

    def user_bookmark_count_authorization(self):
        """If no API_KEY is present, it is unauthorized request"""
        self.testapp.get(u'/api/v1/admin/stats/bmarkcount',
                         status=403)

    def test_account_information(self):
        """Test getting a user's account information"""
        res = self.testapp.get(u'/api/v1/admin/account?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        self.assertEqual(
            user['username'], 'admin',
            "Should have a username of admin {0}".format(user))

        self.assertTrue(
            'password' not in user,
            'Should not have a field password {0}'.format(user))
        self.assertTrue(
            '_password' not in user,
            'Should not have a field password {0}'.format(user))
        self.assertTrue(
            'api_key' not in user,
            'Should not have a field password {0}'.format(user))
        self._check_cors_headers(res)

    def test_account_update(self):
        """Test updating a user's account information"""
        params = {
            'name': u'Test Admin'
        }
        res = self.testapp.post(
            str(u"/api/v1/admin/account?api_key=" + str(API_KEY)),
            content_type='application/json',
            params=json.dumps(params),
            status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        self.assertEqual(
            user['username'], 'admin',
            "Should have a username of admin {0}".format(user))
        self.assertEqual(
            user['name'], 'Test Admin',
            "Should have a new name of Test Admin {0}".format(user))

        self.assertTrue(
            'password' not in user,
            "Should not have a field password {0}".format(user))
        self.assertTrue(
            '_password' not in user,
            "Should not have a field password {0}".format(user))
        self.assertTrue(
            'api_key' not in user,
            "Should not have a field password {0}".format(user))
        self._check_cors_headers(res)

    def test_account_apikey(self):
        """Fetching a user's api key"""
        res = self.testapp.get(
            u"/api/v1/admin/api_key?api_key=" + str(API_KEY),
            status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        self.assertEqual(
            user['username'], 'admin',
            "Should have a username of admin {0}".format(user))
        self.assertTrue(
            'api_key' in user,
            "Should have an api key in there: {0}".format(user))
        self._check_cors_headers(res)

    def test_account_reset_apikey(self):
        """Reset User's api key"""

        # Create a fake user
        test_user = factory.make_user(username='test_user')
        # Set and Get the current api key
        # make_user doesn't set the api key of user so set it explicitly
        current_apikey = test_user.api_key = "random_key"
        test_user.activation = Activation(u'signup')
        transaction.commit()

        # send a request to reset the api key
        res = self.testapp.post(
            "/api/v1/test_user/api_key?api_key=" + current_apikey,
            content_type='application/json',
            params={u'username': 'test_user',
                    u'api_key': current_apikey},
            status=200)

        # Get the user's api key from db
        fetch_api = DBSession.execute(
            "SELECT api_key FROM users WHERE username='test_user'").fetchone()
        new_apikey = fetch_api['api_key']

        # make sure we can decode the body
        response = json.loads(res.body)

        # old and new api keys must not be the same
        self.assertNotEqual(
            current_apikey, new_apikey,
            "Api key must be changed after reset request")
        self.assertTrue(
            'api_key' in response,
            "Should have an api key in there: {0}".format(response))

        # Api key in response must be the new one
        self.assertEqual(
            response['api_key'], new_apikey,
            "Should have a api key of user {0}".format(response))

        self._check_cors_headers(res)

    def test_account_password_change(self):
        """Change a user's password"""
        params = {
            'current_password': 'admin',
            'new_password': 'not_testing'
        }

        res = self.testapp.post(
            "/api/v1/admin/password?api_key=" + str(API_KEY),
            params=params,
            status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        self.assertEqual(
            user['username'], 'admin',
            "Should have a username of admin {0}".format(user))
        self.assertTrue(
            'message' in user,
            "Should have a message key in there: {0}".format(user))

        params = {
            'current_password': 'not_testing',
            'new_password': 'admin'
        }
        res = self.testapp.post(
            "/api/v1/admin/password?api_key=" + str(API_KEY),
            params=params,
            status=200)

        self._check_cors_headers(res)

    def test_account_password_failure(self):
        """Change a user's password, in bad ways"""
        params = {
            'current_password': 'test',
            'new_password': 'not_testing'
        }

        res = self.testapp.post(
            "/api/v1/admin/password?api_key=" + str(API_KEY),
            params=params,
            status=403)

        # make sure we can decode the body
        user = json.loads(res.body)

        self.assertEqual(
            user['username'], 'admin',
            "Should have a username of admin {0}".format(user))
        self.assertTrue(
            'error' in user,
            "Should have a error key in there: {0}".format(user))
        self.assertTrue(
            'typo' in user['error'],
            "Should have a error key in there: {0}".format(user))
        self._check_cors_headers(res)

    def test_api_ping_success(self):
        """We should be able to ping and make sure we auth'd and are ok"""
        res = self.testapp.get('/api/v1/admin/ping?api_key=' + API_KEY,
                               status=200)
        ping = json.loads(res.body)

        self.assertTrue(ping['success'])

        self._check_cors_headers(res)

    def test_api_ping_failed_invalid_api(self):
        """If you don't supply a valid api key, you've failed the ping"""

        # Login a user and then test the validation of api key

        user_data = {'login': u'admin',
                     'password': u'admin',
                     'form.submitted': u'true'}

        # Assuming user logged in without errors
        self.testapp.post('/login', params=user_data)

        # Check for authentication of api key

        res = self.testapp.get('/api/v1/admin/ping?api_key=' + 'invalid',
                               status=200)
        ping = json.loads(res.body)

        self.assertFalse(ping['success'])
        self.assertEqual(ping['message'], "API key is invalid.")
        self._check_cors_headers(res)

    def test_api_ping_failed_nouser(self):
        """If you don't supply a username, you've failed the ping"""
        res = self.testapp.get('/api/v1/ping?api_key=' + API_KEY,
                               status=200)
        ping = json.loads(res.body)

        self.assertTrue(not ping['success'])
        self.assertEqual(ping['message'], "Missing username in your api url.")
        self._check_cors_headers(res)

    def test_api_ping_failed_missing_api(self):
        """If you don't supply a username, you've failed the ping"""
        res = self.testapp.get('/ping?api_key=' + API_KEY,
                               status=200)
        ping = json.loads(res.body)

        self.assertTrue(not ping['success'])
        self.assertEqual(ping['message'], "The API url should be /api/v1")
        self._check_cors_headers(res)

    def test_bookmarks_stats(self):
        """Test the bookmark stats"""
        res = self.testapp.get(u'/api/v1/stats/bookmarks',
                               status=200)
        data = json.loads(res.body)
        self.assertTrue(
            'count' in data,
            "Should have bookmark count: " + str(data))
        self.assertTrue(
            'unique_count' in data,
            "Should have unique bookmark count: " + str(data))

    def test_user_stats(self):
        """Test the user stats"""
        res = self.testapp.get(u'/api/v1/stats/users',
                               status=200)
        data = json.loads(res.body)
        self.assertTrue(
            'count' in data,
            "Should have user count: " + str(data))
        self.assertTrue(
            'activations' in data,
            "Should have pending user activations: " + str(data))
        self.assertTrue(
            'with_bookmarks' in data,
            "Should have count of users with bookmarks: " + str(data))

    def test_tag_search_casing(self):
        """Test that search works same with all types of casing"""

        # Adding the tags 'python' and 'search'
        self._get_good_request()

        # Testing the tag 'python' and 'search' with different cases
        word_list = ['python', 'Python', 'pYthon', 'PYTHoN', 'pythON',
                     'PythON', 'pYthON', 'PYthON', 'pYTHON', 'PYTHON']
        word_list += ['search', 'Search', 'sEARCh', 'SEARCh', 'searcH',
                      'searCH', 'SearCH', 'sEarCH', 'seARCH', 'SEARCH']

        for word in word_list:
            res = self.testapp.get(
                u'/api/v1/admin/bmarks/{0}?&api_key={1}'.format(
                    word, API_KEY),
                status=200)
            data = json.loads(res.body)

            self.assertTrue(
                data['count'] > 0,
                "Should have found > 0 bookmarks")

        self._check_cors_headers(res)

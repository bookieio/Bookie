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

GOOGLE_HASH = 'aa2239c17609b2'
BMARKUS_HASH = 'c5c21717c99797'
LOG = logging.getLogger(__name__)

API_KEY = None


class BookieAPITest(unittest.TestCase):
    """Test the Bookie API"""

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app(BOOKIE_TEST_INI, 'main')
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

    def _get_good_request(self, content=False, second_bmark=False):
        """Return the basics for a good add bookmark request"""
        session = DBSession()

        # the main bookmark, added second to prove popular will sort correctly
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': API_KEY,
                'username': 'admin',
                'inserted_by': 'chrome_ext',
        }

        # if we want to test the readable fulltext side we want to make sure we
        # pass content into the new bookmark
        if content:
            prms['content'] = "<h1>There's some content in here dude</h1>"

        # req_params = urllib.urlencode(prms)
        res = self.testapp.post('/api/v1/admin/bmark?',
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
                    'username': 'admin',
                    'inserted_by': 'chrome_ext',
            }

            # if we want to test the readable fulltext side we want to make
            # sure we pass content into the new bookmark
            prms['content'] = "<h1>Second bookmark man</h1>"

            # req_params = urllib.urlencode(prms)
            res = self.testapp.post('/api/v1/admin/bmark?',
                                    content_type='application/json',
                                    params=json.dumps(prms)
            )

        session.flush()
        transaction.commit()
        return res

    def test_add_bookmark(self):
        """We should be able to add a new bookmark to the system"""
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
        }

        res = self.testapp.post('/api/v1/admin/bmark',
                                params=test_bmark,
                                status=200)

        ok_('"location":' in res.body,
                "Should have a location result: " + res.body)
        ok_('description": "Bookie"' in res.body,
                "Should have Bookie in description: " + res.body)

    def test_bookmark_fetch(self):
        """Test that we can get a bookmark and it's details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/admin/bmark/{0}?api_key={1}'.format(
                               GOOGLE_HASH,
                               API_KEY),
                               status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmark']
        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        ok_(u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        ok_(bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" + \
                str(bmark[u'tags'][0][u'name']))

        ok_(u'readable' not in bmark,
            "We should not have readable content")

        eq_(u'python search', bmark[u'tag_str'],
                "tag_str should be populated: " + str(dict(bmark)))

        # to get readble content we need to pass the flash with_content
        res = self.testapp.get(
            '/api/v1/admin/bmark/{0}?api_key={1}&with_content=true'.format(
            GOOGLE_HASH,
            API_KEY),
            status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmark']

        ok_(u'readable' in bmark,
            "We should have readable content")

        ok_('dude' in bmark['readable']['content'],
            "We should have 'dude' in our content: " + \
                bmark['readable']['content'])

    def test_bookmark_fetch_fail(self):
        """Verify we get a failed response when wrong bookmark"""
        self._get_good_request()

        # test that we get a 404
        self.testapp.get('/api/v1/admin/bmark/{0}?api_key={1}'.format(
                             BMARKUS_HASH,
                             API_KEY),
                         status=404)

    def test_bookmark_remove(self):
        """A delete call should remove the bookmark from the system"""
        self._get_good_request(content=True, second_bmark=True)

        # now let's delete the google bookmark
        res = self.testapp.delete('/api/v1/admin/bmark/{0}?api_key={1}'.format(
                                    GOOGLE_HASH,
                                    API_KEY),
                                    status=200)

        ok_('message": "done"' in res.body,
                "Should have a message of done: " + res.body)

        # we're going to cheat like mad, use the sync call to get the hash_ids
        # of bookmarks in the system and verify that only the bmark.us hash_id
        # is in the response body
        res = self.testapp.get('/api/v1/admin/extension/sync',
                               params={'api_key': API_KEY},
                               status=200)

        ok_(GOOGLE_HASH not in res.body,
                "Should not have the google hash: " + res.body)
        ok_(BMARKUS_HASH in res.body,
                "Should have the bmark.us hash: " + res.body)

    def test_bookmark_recent_user(self):
        """Test that we can get list of bookmarks with details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/admin/bmarks?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmarks'][0]
        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        ok_(u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        ok_(bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" + \
                str(bmark[u'tags'][0][u'name']))

        res = self.testapp.get(
            '/api/v1/admin/bmarks?with_content=true&api_key=' + API_KEY,
            status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmarks'][0]
        ok_('here dude' in bmark[u'readable']['content'],
            "There should be content: " + str(bmark))

    def test_bookmark_recent(self):
        """Test that we can get list of bookmarks with details"""
        self._get_good_request(content=True)
        res = self.testapp.get('/api/v1/bmarks?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmarks'][0]
        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id should match: " + str(bmark[u'hash_id']))

        ok_(u'tags' in bmark,
            "We should have a list of tags in the bmark returned")

        ok_(bmark[u'tags'][0][u'name'] in [u'python', u'search'],
            "Tag should be either python or search:" + \
                str(bmark[u'tags'][0][u'name']))

        res = self.testapp.get(
            '/api/v1/admin/bmarks?with_content=true&api_key=' + API_KEY,
            status=200)

        # make sure we can decode the body
        bmark = json.loads(res.body)['bmarks'][0]
        ok_('here dude' in bmark[u'readable']['content'],
            "There should be content: " + str(bmark))

    def test_bookmark_sync(self):
        """Test that we can get the sync list from the server"""
        self._get_good_request(content=True, second_bmark=True)

        # test that we only get one resultback
        res = self.testapp.get('/api/v1/admin/extension/sync',
                               params={'api_key': API_KEY},
                               status=200)

        eq_(res.status, "200 OK",
                msg='Get status is 200, ' + res.status)

        ok_(GOOGLE_HASH in res.body,
                "The google hash id should be in the json: " + res.body)
        ok_(BMARKUS_HASH in res.body,
                "The bmark.us hash id should be in the json: " + res.body)

    def test_search_api(self):
        """Test that we can get list of bookmarks ordered by clicks"""
        self._get_good_request(content=True, second_bmark=True)

        res = self.testapp.get('/api/v1/bmarks/search/google', status=200)

        # make sure we can decode the body
        bmark_list = json.loads(res.body)
        results = bmark_list['search_results']
        eq_(len(results), 1,
            "We should have one result coming back: {0}".format(len(results)))

        bmark = results[0]

        eq_(GOOGLE_HASH, bmark[u'hash_id'],
            "The hash_id {0} should match: {1} ".format(
                str(GOOGLE_HASH),
                str(bmark[u'hash_id'])))

        ok_('clicks' in bmark,
            "The clicks field should be in there")

    def test_bookmark_tag_complete(self):
        """Test we can complete tags in the system

        By default we should have tags for python, search, bookmarks

        """
        self._get_good_request(second_bmark=True)

        res = self.testapp.get('/api/v1/admin/tags/complete',
                          params={'tag': 'py',
                                  'api_key': API_KEY},
                          status=200)

        ok_('python' in res.body,
                "Should have python as a tag completion: " + res.body)

        # we shouldn't get python as an option if we supply bookmarks as the
        # current tag. No bookmarks have both bookmarks & python as tags
        res = self.testapp.get('/api/v1/admin/tags/complete',
                               params={'tag': 'py',
                                       'current': 'bookmarks',
                                       'api_key': API_KEY
                               },
                               status=200)

        ok_('python' not in res.body,
                "Should not have python as a tag completion: " + res.body)

    def test_account_information(self):
        """Test getting a user's account information"""
        res = self.testapp.get('/api/v1/admin/account?api_key=' + API_KEY,
                               status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        eq_(user['username'], 'admin',
                "Should have a username of admin {0}".format(user))

        ok_('password' not in user,
                "Should not have a field password {0}".format(user))
        ok_('_password' not in user,
                "Should not have a field password {0}".format(user))
        ok_('api_key' not in user,
                "Should not have a field password {0}".format(user))

    def test_account_update(self):
        """Test updating a user's account information"""
        params = {
            'name': u'Test Admin'
        }
        res = self.testapp.post(
            str("/api/v1/admin/account?api_key=" + str(API_KEY)),
            content_type='application/json',
            params=json.dumps(params),
            status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        eq_(user['username'], 'admin',
                "Should have a username of admin {0}".format(user))
        eq_(user['name'], 'Test Admin',
                "Should have a new name of Test Admin {0}".format(user))

        ok_('password' not in user,
                "Should not have a field password {0}".format(user))
        ok_('_password' not in user,
                "Should not have a field password {0}".format(user))
        ok_('api_key' not in user,
                "Should not have a field password {0}".format(user))

    def test_account_apikey(self):
        """Fetching a user's api key"""
        res = self.testapp.get("/api/v1/admin/api_key?api_key=" + str(API_KEY),
                               status=200)

        # make sure we can decode the body
        user = json.loads(res.body)

        eq_(user['username'], 'admin',
                "Should have a username of admin {0}".format(user))
        ok_('api_key' in user,
                "Should have an api key in there: {0}".format(user))

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

        eq_(user['username'], 'admin',
                "Should have a username of admin {0}".format(user))
        ok_('message' in user,
                "Should have a message key in there: {0}".format(user))

        params = {
                'current_password': 'not_testing',
                'new_password': 'admin'
        }
        res = self.testapp.post(
            "/api/v1/admin/password?api_key=" + str(API_KEY),
            params=params,
            status=200)

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

        eq_(user['username'], 'admin',
                "Should have a username of admin {0}".format(user))
        ok_('error' in user,
                "Should have a error key in there: {0}".format(user))
        ok_('typo' in user['error'],
                "Should have a error key in there: {0}".format(user))




    # def test_paging_results(self):
    #     """Test that we can page results"""
    #     self._get_good_request(content=True, second_bmark=True)

    #     # test that we only get one resultback
    #     res = self.testapp.get('/admin/api/v1/bmarks/recent?page=0&count=1')

    #     eq_(res.status, "200 OK",
    #             msg='Get status is 200, ' + res.status)

    #     # make sure we can decode the body
    #     bmarks = json.loads(res.body)['payload']['bmarks']

    #     eq_(len(bmarks), 1, "We should only have one result in this page")

    #     res = self.testapp.get('/admin/api/v1/bmarks/recent?page=1&count=1')

    #     eq_(res.status, "200 OK",
    #             msg='Get status is 200, ' + res.status)

    #     # make sure we can decode the body
    #     bmarks = json.loads(res.body)['payload']['bmarks']

    #     eq_(len(bmarks), 1,
    #         "We should only have one result in the second page")

    #     res = self.testapp.get('/admin/api/v1/bmarks/recent?page=2&count=1')

    #     eq_(res.status, "200 OK",
    #             msg='Get status is 200, ' + res.status)

    #     # make sure we can decode the body
    #     bmarks = json.loads(res.body)['payload']['bmarks']

    #     eq_(len(bmarks), 0,
    #         "We should not have any results for page 2")



    # def test_bookmark_add(self):
    #     """We should be able to add a new bookmark to the system"""
    #     test_bmark = {
    #             'url': u'http://bmark.us',
    #             'description': u'Bookie',
    #             'extended': u'Extended notes',
    #             'tags': u'bookmarks',
    #             'api_key': API_KEY,
    #     }

    #     res = self.testapp.post('/admin/api/v1/bmarks/add',
    #         params=test_bmark,
    #         status=200)

    #     ok_('"success": true' in res.body,
    #             "Should have a success of true: " + res.body)
    #     ok_('message": "done"' in res.body,
    #             "Should have a done message: " + res.body)

    # def test_bookmark_add_bad_key(self):
    #     """We should be able to add a new bookmark to the system"""
    #     test_bmark = {
    #             'url': u'http://bmark.us',
    #             'description': u'Bookie',
    #             'extended': u'Extended notes',
    #             'tags': u'bookmarks',
    #             'api_key': u'badkey',
    #     }

    #     self.testapp.post('/admin/api/v1/bmarks/add', params=test_bmark,
    #             status=403)

    # def test_bookmark_toread(self):
    #     """A bookmark with !toread command should have toread tag"""

    #     test_bmark = {
    #             'url': u'http://bmark.us',
    #             'description': u'Bookie',
    #             'extended': u'Extended notes',
    #             'tags': u'bookmarks !toread',
    #             'api_key': API_KEY,
    #     }

    #     res = self.testapp.post('/admin/api/v1/bmarks/add',
    #         params=test_bmark,
    #             status=200)

    #     ok_('"success": true' in res.body,
    #             "Should have a success of true: " + res.body)
    #     ok_('message": "done"' in res.body,
    #             "Should have a done message: " + res.body)
    #     ok_('!toread' not in res.body,
    #             "Should not have !toread tag: " + res.body)
    #     ok_('toread' in res.body,
    #             "Should have toread tag: " + res.body)

    # def test_bookmark_update_toread(self):
    #     """When marking an existing bookmark !toread, shouldn't lose tags"""
    #     test_bmark = {
    #             'url': u'http://bmark.us',
    #             'description': u'Bookie',
    #             'extended': u'Extended notes',
    #             'tags': u'bookmarks',
    #             'api_key': API_KEY,
    #     }

    #     res = self.testapp.post('/admin/api/v1/bmarks/add',
    #         params=test_bmark,
    #             status=200)

    #     test_bmark['tags'] = u'!toread'

    #     res = self.testapp.post('/admin/api/v1/bmarks/add',
    #         params=test_bmark,
    #                             status=200)

    #     ok_('toread' in res.body,
    #             "Should have added the toread tag: " + res.body)
    #     ok_('bookmarks' in res.body,
    #             "Should still have the bookmarks tag: " + res.body)

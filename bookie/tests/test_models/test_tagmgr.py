"""Test the basics including the bmark and tags"""
import transaction
from pyramid import testing

from bookie.models import (
    Readable,
    DBSession,
    Tag,
    TagMgr,
    BmarkMgr,
)

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests.factory import (
    make_bookmark,
    make_tag,
)

import os


class TestTagMgrStats(TestDBBase):
    """Handle some TagMgr stats checks"""

    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        empty_db()

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        for i in range(ct):
            t = Tag(gen_random_word(10))
            DBSession.add(t)

        ct = TagMgr.count()
        self.assertEqual(5, ct, 'We should have a total of 5: ' + str(ct))

    def test_basic_complete(self):
        """Tags should provide completion options."""
        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str)

        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

    def test_case_insensitive(self):
        """Suggestion does not care about case of the prefix."""
        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        test_str = tags[0].name[0:4].upper()
        suggestions = TagMgr.complete(test_str)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

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
        path = os.getcwd()+"/bookie/tests/test_models/tag_test.txt"
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
        path = os.getcwd() + "/bookie/tests/test_models/tag_test.txt"
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

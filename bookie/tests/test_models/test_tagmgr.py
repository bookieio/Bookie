"""Test the basics including the bmark and tags"""
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import TagMgr
from bookie.models import BmarkMgr

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests.factory import make_tag

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
        test_content_file = open(path, 'r')
        content = ""
        for word in test_content_file:
                content += word
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
        tags_expected = ['network', 'simulator', 'NS', 'user', 'project']
        edit_bmark = {
            'hash_id': hash_id,
            'username': 'admin',
            'url': url
        }
        hash_id = str(hash_id)
        res = self.testapp.post('/admin/edit/'+hash_id,
                                params=edit_bmark,
                                status=200)
        for tag in tags_expected:
            self.assertIn(tag, res.body)

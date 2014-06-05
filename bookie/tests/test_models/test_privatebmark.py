"""Test private bookmark support"""

from pyramid import testing

from bookie.models import (
    Bmark,
    BmarkMgr,
)
from bookie.models.auth import User

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestPrivateBmark(TestDBBase):
    """Handle private bookmark checks"""

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

    def test_is_private_default(self):
        """Verify the default value of is_private"""
        user = User()
        user.username = gen_random_word(10)
        bmark = Bmark(
            url=gen_random_word(12),
            username=user.username
        )
        self.assertEqual(
            True,
            bmark.is_private,
            'Default value of is_private should be True')

    def test_is_private_true(self):
        """Verify the value of is_private is True"""
        user = User()
        user.username = gen_random_word(10)
        bmark = Bmark(
            url=gen_random_word(12),
            username=user.username,
            is_private=True
        )
        self.assertEqual(
            True,
            bmark.is_private)

    def test_is_private_false(self):
        """Verify the value of is_private is False"""
        user = User()
        user.username = gen_random_word(10)
        bmark = Bmark(
            url=gen_random_word(12),
            username=user.username,
            is_private=False
        )
        self.assertEqual(
            False,
            bmark.is_private)

    def test_storing_private_true(self):
        """Verify the value of is_private defaults to True"""
        user = User()
        user.username = gen_random_word(10)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'
        bmark_tags = u'python test'
        bmark = BmarkMgr.store(
            url=bmark_url,
            username=user.username,
            desc=bmark_desc,
            ext=bmark_ext,
            tags=bmark_tags
        )
        self.assertEqual(
            True,
            bmark.is_private)

    def test_storing_private_false(self):
        """Verify the value of is_private is False"""
        user = User()
        user.username = gen_random_word(10)
        bmark_url = u'http://bmark.us'
        bmark_desc = u'This is a test bookmark'
        bmark_ext = u'Some extended notes'
        bmark_tags = u'python test'
        bmark = BmarkMgr.store(
            url=bmark_url,
            username=user.username,
            desc=bmark_desc,
            ext=bmark_ext,
            tags=bmark_tags,
            is_private=False
        )
        self.assertEqual(
            False,
            bmark.is_private)

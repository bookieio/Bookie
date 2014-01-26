"""Test the basics including the bmark and tags"""
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import TagMgr

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests.factory import make_tag


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

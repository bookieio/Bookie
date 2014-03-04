"""Test the basics including the bmark and tags"""

from random import randint
from pyramid import testing

from bookie.models import (
    DBSession,
    Bmark,
    BmarkMgr,
    TagMgr,
)
from bookie.models.auth import User

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestBmarkMgrStats(TestDBBase):
    """Handle some bmarkmgr stats checks"""

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
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        for i in range(ct):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username
            )
            b.hash_id = gen_random_word(3)
            DBSession.add(b)

        ct = BmarkMgr.count()
        self.assertEqual(5, ct, 'We should have a total of 5: ' + str(ct))

    def test_unique_ct(self):
        """Verify that our unique count method is working"""
        ct = 5
        common = u'testing.com'
        users = []
        for i in range(ct):
            user = User()
            user.username = gen_random_word(10)
            DBSession.add(user)
            users.append(user)

        for i in range(ct - 2):
            b = Bmark(
                url=gen_random_word(12),
                username=users[i].username
            )
            DBSession.add(b)

        # Add in our dupes
        c = Bmark(
            url=common,
            username=users[3].username
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=common,
            username=users[4].username
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(distinct=True)
        self.assertEqual(4, ct, 'We should have a total of 4: ' + str(ct))

    def test_per_user(self):
        """We should only get a pair of results for this single user"""
        ct = 5
        common = u'testing.com'
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)

        usercommon = User()
        usercommon.username = common
        DBSession.add(usercommon)

        for i in range(ct - 2):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username
            )
            DBSession.add(b)

        # add in our dupes
        c = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(username=usercommon.username)
        self.assertEqual(2, ct, 'We should have a total of 2: ' + str(ct))

    def test_delete_all_bookmarks(self):
        """Testing working of delete all bookmarks
                Case 1: No bookmark present
                Case 2: One bookmark present
                Case 3: Multiple bookmarks present"""

        bmark_counts = [0, 1]
        for i in range(10):
            bmark_counts.append(randint(10, 100))

        users = []
        for i in range(len(bmark_counts)):
            user = User()
            user.username = gen_random_word(10)
            users.append(user)

            DBSession.add(user)
            for j in range(i):
                b = Bmark(
                    url=gen_random_word(12),
                    username=user.username,
                    tags=gen_random_word(4),
                )
                b.hash_id = gen_random_word(3)
                DBSession.add(b)

        DBSession.flush()

        for user in users:
            BmarkMgr.delete_all_bookmarks(user.username)
            ct = BmarkMgr.count(user.username)
            self.assertEqual(ct, 0, 'All the bookmarks should be deleted')
            tags = TagMgr.find(username=user.username)
            self.assertEqual(
                len(tags),
                0,
                'There should be no tags left: ' + str(len(tags))
            )
            DBSession.flush()

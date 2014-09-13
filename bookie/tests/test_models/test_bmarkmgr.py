"""Test the basics including the bmark and tags"""

from random import randint

from bookie.models import (
    Bmark,
    BmarkMgr,
    DBSession,
    TagMgr,
)
from bookie.models.auth import User
from bookie.models.stats import (
    StatBookmark,
    StatBookmarkMgr,
)

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestBmarkMgrStats(TestDBBase):
    """Handle some bmarkmgr stats checks"""

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        for i in range(ct):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=False
            )
            b.hash_id = gen_random_word(3)
            DBSession.add(b)

        ct = BmarkMgr.count()
        self.assertEqual(5, ct,
                         'We should have 5 public bookmarks: ' + str(ct))

    def test_total_ct_accounts_for_privacy(self):
        """Verify that our total count method is working"""
        ct = 5
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        for i in range(ct):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=True
            )
            b.hash_id = gen_random_word(3)
            DBSession.add(b)

        ct = BmarkMgr.count(is_private=True)
        self.assertEqual(5, ct,
                         'We should have 5 private bookmarks: ' + str(ct))

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
                username=users[i].username,
                is_private=False
            )
            DBSession.add(b)

        # Add in our dupes
        c = Bmark(
            url=common,
            username=users[3].username,
            is_private=False
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=common,
            username=users[4].username,
            is_private=False
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(distinct=True)
        self.assertEqual(4, ct,
                         'We should have 4 public bookmarks: ' + str(ct))

    def test_unique_ct_accounts_for_privacy(self):
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
                username=users[i].username,
                is_private=True
            )
            DBSession.add(b)

        # Add in our dupes
        c = Bmark(
            url=common,
            username=users[3].username,
            is_private=True
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=common,
            username=users[4].username,
            is_private=True,
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(distinct=True, is_private=True)
        self.assertEqual(4, ct,
                         'We should have 4 private bookmarks: ' + str(ct))

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
                username=user.username,
                is_private=False
            )
            DBSession.add(b)

        # add in our dupes
        c = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
            is_private=False
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
            is_private=False
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(username=usercommon.username)
        self.assertEqual(2, ct,
                         'We should have 2 public bookmarks: ' + str(ct))

    def test_per_user_accounts_for_privacy(self):
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
                username=user.username,
                is_private=True,
            )
            DBSession.add(b)

        c = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
            is_private=True,
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=gen_random_word(10),
            username=usercommon.username,
            is_private=True,
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(username=usercommon.username, is_private=True)
        self.assertEqual(2, ct,
                         'We should only have 2 private bookmarks: ' + str(ct))

    def test_count_user_bookmarks(self):
        """We should get a total count of both private and public bookmarks"""
        public_bmark_count = 5
        private_bmark_count = 5
        total_bmark_count = public_bmark_count + private_bmark_count
        user = User()
        user.username = gen_random_word(10)
        DBSession.add(user)
        stat_username = "user_bookmarks_{0}".format(user.username)

        # Add the public bookmarks.
        for i in range(public_bmark_count):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=False,
            )
            DBSession.add(b)

        # Add the private bookmarks.
        for i in range(private_bmark_count):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=True,
            )
            DBSession.add(b)

        StatBookmarkMgr.count_user_bookmarks(username=user.username)
        res = DBSession.query(StatBookmark).\
            filter(StatBookmark.attrib == stat_username).first()

        self.assertEqual(
            total_bmark_count, res.data,
            'We should have {0} bookmarks: '.format(total_bmark_count) +
            str(res.data))

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

    def test_find_bookmarks_same_user(self):
        """A user requesting their bookmarks includes private ones"""
        bookmark_count_private = 5
        bookmark_count_public = 5
        user = User()
        user.username = gen_random_word(19)
        DBSession.add(user)

        for i in range(bookmark_count_private):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
            )
            DBSession.add(b)

        for i in range(bookmark_count_public):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=False,
            )
            DBSession.add(b)

        DBSession.flush()
        res = BmarkMgr.find(username=user.username, requested_by=user.username)
        self.assertEqual(
            bookmark_count_private + bookmark_count_public,
            len(res),
            'There should be ' + str(bookmark_count_private +
                                     bookmark_count_public) +
            ' bookmarks present: ' + str(len(res))
        )

    def test_find_bookmarks_diff_user(self):
        """A user requesting another user's bookmarks get public only"""
        bookmark_count_private = 5
        bookmark_count_public = 5
        user = User()
        user.username = gen_random_word(19)
        DBSession.add(user)

        for i in range(bookmark_count_private):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=True,
            )
            DBSession.add(b)

        for i in range(bookmark_count_public):
            b = Bmark(
                url=gen_random_word(12),
                username=user.username,
                is_private=False,
            )
            DBSession.add(b)

        DBSession.flush()
        res = BmarkMgr.find(username=user.username,
                            requested_by=gen_random_word(19))
        self.assertEqual(
            bookmark_count_public,
            len(res),
            'There should be ' + str(bookmark_count_public) +
            ' bookmarks present: ' + str(len(res))
        )

        # Also check if requested_by is None.
        res = BmarkMgr.find(username=user.username, requested_by=None)
        self.assertEqual(
            bookmark_count_public,
            len(res),
            'There should be ' + str(bookmark_count_public) +
            ' bookmarks present: ' + str(len(res))
        )

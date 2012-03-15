"""Test the basics including the bmark and tags"""
from nose.tools import eq_

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestBmarkMgrStats(TestDBBase):
    """Handle some bmarkmgr stats checks"""

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        for i in range(ct):
            b = Bmark(
                url=gen_random_word(12),
                username=gen_random_word(10)
            )
            b.hash_id = gen_random_word(3)
            DBSession.add(b)

        ct = BmarkMgr.count()
        eq_(5, ct, 'We should have a total of 5: ' + str(ct))

    def test_unique_ct(self):
        """Verify that our unique count method is working"""
        ct = 5
        common = 'testing.com'
        for i in range(ct - 2):
            b = Bmark(
                url=gen_random_word(12),
                username=gen_random_word(10)
            )
            DBSession.add(b)

        # add in our dupes
        c = Bmark(
            url=common,
            username=gen_random_word(10)
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=common,
            username=gen_random_word(10)
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(distinct=True)
        eq_(4, ct, 'We should have a total of 4: ' + str(ct))

    def test_per_user(self):
        """We should only get a pair of results for this single user"""
        ct = 5
        common = 'testing.com'
        for i in range(ct - 2):
            b = Bmark(
                url=gen_random_word(12),
                username=gen_random_word(10)
            )
            DBSession.add(b)

        # add in our dupes
        c = Bmark(
            url=gen_random_word(10),
            username=common,
        )
        DBSession.add(c)
        DBSession.flush()

        d = Bmark(
            url=gen_random_word(10),
            username=common,
        )
        DBSession.add(d)
        DBSession.flush()

        ct = BmarkMgr.count(username=common)
        eq_(2, ct, 'We should have a total of 2: ' + str(ct))

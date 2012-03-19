"""Test the basics including the bmark and tags"""
from nose.tools import eq_

from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import TagMgr

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestTagMgrStats(TestDBBase):
    """Handle some TagMgr stats checks"""

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        for i in range(ct):
            t = Tag(gen_random_word(10))
            DBSession.add(t)

        ct = TagMgr.count()
        eq_(5, ct, 'We should have a total of 5: ' + str(ct))



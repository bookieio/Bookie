"""Test the basics including the bmark and tags"""
import transaction
import unittest

from nose.tools import ok_
from nose.tools import eq_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import TagMgr

from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class TestBmarkMgr(TestDBBase):
    """Handle some bmarkmgr checks"""

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

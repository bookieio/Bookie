"""Tests that we make sure our export functions work"""
import logging

import transaction
import unittest
import urllib

from nose.tools import ok_
from pyramid import testing

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Tag, bmarks_tags


LOG = logging.getLogger(__name__)
API_KEY = None

class TestExport(unittest.TestCase):
    """Test the web export"""

    def _get_good_request(self):
        """Return the basics for a good add bookmark request"""
        session = DBSession()
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
                'api_key': API_KEY,
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.get('/admin/api/v1/bmarks/add?',
                               params=req_params,)
        session.flush()
        transaction.commit()
        return res

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()
        global API_KEY
        res = DBSession.execute("SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        API_KEY = res['api_key']

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        session = DBSession
        Bmark.query.delete()
        Tag.query.delete()
        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()

    def test_export(self):
        """Test that we can upload/import our test file"""
        self._get_good_request()

        res = self.testapp.post('/admin/export',
                                status=200)

        ok_("google.com" in res.body,
                msg='Google is in the exported body: ' +  res.body)

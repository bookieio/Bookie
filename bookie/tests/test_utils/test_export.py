"""Tests that we make sure our export functions work"""
import json
import logging

import transaction
import unittest
import urllib

from pyramid import testing

from bookie.models import DBSession
from bookie.tests import empty_db


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
            'api_key': API_KEY
        }

        req_params = urllib.urlencode(prms)
        res = self.testapp.post('/api/v1/admin/bmark?api_key=' + API_KEY,
                                params=req_params,)
        session.flush()
        transaction.commit()
        return res

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()
        global API_KEY
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        API_KEY = str(res['api_key'])

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()
        empty_db()

    def test_export(self):
        """Test that we can upload/import our test file"""
        self._get_good_request()

        res = self.testapp.get(
            '/api/v1/admin/bmarks/export?api_key=' + API_KEY,
            status=200)

        self.assertTrue(
            "google.com" in res.body,
            msg='Google is in the exported body: ' + res.body)
        data = json.loads(res.body)

        self.assertEqual(
            1,
            data['count'],
            "Should be one result: " + str(data['count']))

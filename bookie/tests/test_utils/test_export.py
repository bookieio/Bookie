"""Tests that we make sure our export functions work"""
import json
import logging

import urllib

from bookie.tests import TestViewBase


LOG = logging.getLogger(__name__)
API_KEY = None


class TestExport(TestViewBase):
    """Test the web export"""

    def _get_good_request(self, is_private=False):
        """Return the basics for a good add bookmark request"""
        prms = {
            'url': u'http://google.com',
            'description': u'This is my google desc',
            'extended': u'And some extended notes about it in full form',
            'tags': u'python search',
            'is_private': is_private,
        }

        res = self.app.post(
            '/api/v1/admin/bmark?api_key={0}'.format(self.api_key),
            content_type='application/json',
            params=json.dumps(prms),
        )
        return res

    def _get_good_request_wo_tags(self):
        """Return the basics for a good add bookmark request
            without any tags"""
        prms = {
            'url': u'http://bmark.us',
            'description': u'This is my bmark desc',
            'extended': u'And some extended notes about it in full form',
            'tags': u'',
        }

        req_params = urllib.urlencode(prms)
        res = self.app.post(
            '/api/v1/admin/bmark?api_key={0}'.format(self.api_key),
            params=req_params,
        )
        return res

    def test_export(self):
        """Test that we can upload/import our test file"""
        self._get_good_request()

        res = self.app.get(
            '/api/v1/admin/bmarks/export?api_key={0}'.format(
                self.api_key),
            status=200)

        self.assertTrue(
            "google.com" in res.body,
            msg='Google is in the exported body: ' + res.body)
        data = json.loads(res.body)

        self.assertEqual(
            1,
            data['count'],
            "Should be one result: " + str(data['count']))

    def test_export_wo_tags(self):
        """Test that we can upload/import our test file"""
        self._get_good_request_wo_tags()

        res = self.app.get(
            '/api/v1/admin/bmarks/export?api_key={0}'.format(
                self.api_key),
            status=200)

        self.assertTrue(
            "bmark.us" in res.body,
            msg='Bmark is in the exported body: ' + res.body)
        data = json.loads(res.body)

        self.assertEqual(
            1,
            data['count'],
            "Should be one result: " + str(data['count']))

    def test_export_view(self):
        """Test that we get IS_PRIVATE attribute for each bookmark during
        export"""
        self._get_good_request()

        res = self.app.get('/admin/export', status=200)

        self.assertTrue(
            "google.com" in res.body,
            msg='Google is in the exported body: ' + res.body)

        self.assertTrue(
            'PRIVATE="1"' not in res.body,
            "Bookmark should be a public bookmark: " + res.body)

    def test_export_view_accounts_for_privacy(self):
        """Test that we get IS_PRIVATE attribute for each bookmark during
        export"""
        self._get_good_request(is_private=True)

        res = self.app.get('/admin/export', status=200)

        self.assertTrue(
            "google.com" in res.body,
            msg='Google is in the exported body: ' + res.body)

        self.assertTrue(
            'PRIVATE="1"' in res.body,
            "Bookmark should be a private bookmark: " + res.body)

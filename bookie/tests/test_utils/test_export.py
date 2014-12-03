"""Tests that we make sure our export functions work"""
import json
import logging
import random

import urllib

from bookie.tests import TestViewBase


LOG = logging.getLogger(__name__)
API_KEY = None


class TestExport(TestViewBase):
    """Test the web export"""

    def _get_good_request(self, is_private=False, url=None, dt=None):
        """Return the basics for a good add bookmark request"""
        if not url:
            url = u'http://google.com'

        prms = {
            'url': url,
            'description': u'This is my google desc',
            'extended': u'And some extended notes about it in full form',
            'tags': u'python search',
            'is_private': is_private,
            'dt': dt
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

    def _get_random_date(self):
        """Returns a random date in ISO 8061 - "%Y-%m-%dT%H:%M:%SZ" format"""
        iso_format = "{year}-{month}-{day}T{hour}:{minute}:{second}Z"
        year_range = [str(i) for i in range(1900, 2014)]
        month_range = [str(i).zfill(2) for i in range(1, 13)]
        day_range = [str(i).zfill(2) for i in range(1, 28)]
        hour_range = [str(i).zfill(2) for i in range(1, 25)]
        min_range = [str(i).zfill(2) for i in range(1, 60)]

        args = {
            "year": random.choice(year_range),
            "month": random.choice(month_range),
            "day": random.choice(day_range),
            "hour": random.choice(hour_range),
            "minute": random.choice(min_range),
            "second": random.choice(min_range)
        }

        return iso_format.format(**args)

    def test_export(self):
        """Test that we can upload/import our test file"""
        self._get_good_request()

        self._login_admin()
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

        self._login_admin()
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

        self._login_admin()
        res = self.app.get('/admin/export?api_key=' + self.api_key, status=200)

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
        self._login_admin()
        res = self.app.get('/admin/export?api_key=' + self.api_key, status=200)

        self.assertTrue(
            "google.com" in res.body,
            msg='Google is in the exported body: ' + res.body)

        self.assertTrue(
            'PRIVATE="1"' in res.body,
            "Bookmark should be a private bookmark: " + res.body)

    def test_export_view_is_sorted(self):
        """Test that we get bookmarks sorted by 'stored' attribute during
        export"""
        self._get_good_request(url=u'https://google.com',
                               dt=self._get_random_date())
        self._get_good_request(url=u'https://twitter.com',
                               dt=self._get_random_date())
        self._get_good_request(url=u'https://github.com',
                               dt=self._get_random_date())

        res = self.app.get(
            '/api/v1/admin/bmarks/export?api_key={0}'.format(
                self.api_key),
            status=200)

        data = json.loads(res.body)

        self.assertEqual(
            3,
            data['count'],
            msg="Should be three results: " + str(data['count']))

        res_bmarks = data['bmarks']
        sorted_bmarks = sorted(res_bmarks,
                               key=lambda k: k['stored'],
                               reverse=True)

        self.assertEqual(
            res_bmarks,
            sorted_bmarks,
            msg="Bookmarks should be sorted in descending order"
        )

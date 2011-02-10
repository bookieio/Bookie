"""Test that we're meeting delicious API specifications"""
import transaction
import unittest
import urllib
from nose.tools import ok_, eq_
from bookie.tests import settings, global_config

from bookie.models import DBSession
from bookie.models import Bmark, NoResultFound


class DelPostTest(unittest.TestCase):
    """Test post related calls"""

    def setUp(self):
        from bookie import main
        app = main(global_config, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
        transaction.begin()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        session = DBSession()
        session.execute('DELETE FROM bmarks')
        session.execute('DELETE FROM tags')
        session.execute('DELETE FROM bmark_tags')
        transaction.commit()

    def _get_good_request(self):
        """Return the basics for a good add bookmark request"""
        prms = {
                'url': u'http://google.com',
                'description': u'This is my google desc',
                'extended': u'And some extended notes about it in full form',
                'tags': u'python search',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/add?' + req_params)
        return res

    def test_post_add_fail(self):
        """Basic add of a new post failing

        Failed response:
            <result code="something went wrong" />

        Not supporting optional params right now
            dt, replace, shared

        """
        failed = '<result code="Bad Request: missing url" />'
        prms = {
                'url': '',
                'description': '',
                'extended': '',
                'tags': '',
        }

        req_params = urllib.urlencode(prms)

        res = self.testapp.get('/delapi/posts/add?' + req_params)
        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, failed, msg="Request should return failed msg: " + res.body)

    def test_post_add_success(self):
        """Basic add of a new post working

        Success response:
            <result code="done" />

        Not supporting optional params right now
            dt, replace, shared

        """
        success = '<result code="done" />'
        res = self._get_good_request()

        eq_(res.status, "200 OK", msg='Post Add status is 200, ' + res.status)
        eq_(res.body, success, msg="Request should return done msg")

    def test_new_bmark(self):
        # go save the thing
        self._get_good_request()

        try:
            res = Bmark.query.filter(Bmark.url == u'http://google.com').one()
            ok_(res, 'We found a result in the db for this bookmark')
            if res:
                return True
            else:
                assert False, "Could not find our bookmark we saved"
        except NoResultFound:
            assert False, "No result found for the bookmark"

#         # now we need to verify the tags got set correctly
#         def _test_new_bmark_tags():
#             """Manually check db for new bmark tags set"""
#             from bookie.models import Bmark
#             res = Bmark.query.filter(Bmark.url == unicode(prms['url'])).one()
#
#             if 'python' in res.tags and 'search' in res.tags:
#                 return True
#             else:
#                 return False
#
#         ok_(_test_new_bmark_tags(), "Found both tags on the bookmark")

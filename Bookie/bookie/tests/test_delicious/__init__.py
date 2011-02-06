"""Test that we're meeting delicious API specifications"""
import unittest
from nose.tools import ok_, eq_
from bookie.tests import _initTestingDB, settings, global_config
from pyramid import testing

class DelAPITest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        _initTestingDB()

        from bookie import main
        app = main(global_config, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)


    def test_root(self):
        res = self.testapp.get('/')
        eq_(res.status, '200 OK')
        ok_('Mako' in res.body, 'Pyramid in the response body')


class DelPostTest(unittest.TestCase):
    """Test post related calls"""

    def setUp(self):
        from bookie import main
        app = main(global_config, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_post_add(self):
        """Basic add of a new post

        Success response:
            <result code="done" />

        Failed response:
            <result code="something went wrong" />

        Not supporting optional params right now
            dt, replace, shared

        """
        success = ""
        failed = '<result code="something went wrong" />'
        prms = {
                'url': '',
                'description': '',
                'extended': '',
                'tags': '',
        }

        in_list = [key + '=' + val for key, val in prms.iteritems()]
        req_params = '&'.join(in_list)

        res = self.testapp.get('/delapi/posts/add?' + req_params)
        eq_(res.status, 200, msg='Post Add status is 200')
        eq_(res.body, failed, msg="Request should return failed msg")

"""Test the auth related web calls"""
import logging

from pyramid import testing
from unittest import TestCase


LOG = logging.getLogger(__name__)


class TestAuthWeb(TestCase):
    """Testing web calls"""

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """We need to empty the bmarks table on each run"""
        testing.tearDown()

    def test_login_url(self):
        """Verify we get the login form"""
        res = self.testapp.get('/login', status=200)

        body_str = u"Log In"
        form_str = u'name="login"'

        self.assertTrue(
            body_str in res.body,
            msg="Request should contain Log In: " + res.body)

        # There should be a login form on there.
        self.assertTrue(
            form_str in res.body,
            msg="The login input should be visible in the body:" + res.body)

    def test_login_success(self):
        """Verify a good login"""

        # the migrations add a default admin account
        user_data = {'login': u'admin',
                     'password': u'admin',
                     'form.submitted': u'true'}

        res = self.testapp.post('/login',
                                params=user_data)
        self.assertEqual(
            res.status,
            "302 Found",
            msg='status is 302 Found, ' + res.status)

        # should end up back at the recent page
        res = res.follow()
        self.assertTrue(
            'recent' in str(res),
            "Should have 'recent' in the resp: " + str(res))

    def test_login_success_username_case_insensitive(self):
        """Verify a good login"""

        # the migrations add a default admin account
        user_data = {'login': u'ADMIN',
                     'password': u'admin',
                     'form.submitted': u'true'}

        res = self.testapp.post('/login',
                                params=user_data)
        self.assertEqual(
            res.status,
            "302 Found",
            msg='status is 302 Found, ' + res.status)

        # should end up back at the recent page
        res = res.follow()
        self.assertTrue(
            'recent' in str(res),
            "Should have 'recent' in the resp: " + str(res))

    def test_login_failure(self):
        """Verify a bad login"""

        # the migrations add a default admin account
        user_data = {'login': u'admin',
                     'password': u'wrongpass',
                     'form.submitted': u'true'}

        res = self.testapp.post('/login',
                                params=user_data)

        self.assertEqual(
            res.status,
            "200 OK",
            msg='status is 200 OK, ' + res.status)

        # should end up back at login with an error message
        self.assertTrue(
            'has failed' in str(res),
            "Should have 'Failed login' in the resp: " + str(res))

    def test_login_null(self):
        """Verify null login form submission fails"""

        user_data = {
            'login': u'',
            'password': u'',
            'form.submitted': u'true'
        }

        res = self.testapp.post('/login',
                                params=user_data)

        self.assertEqual(
            res.status,
            "200 OK",
            msg='status is 200 OK, ' + res.status)

        # should end up back at login with an error message
        self.assertTrue(
            'Failed login' in str(res),
            "Should have 'Failed login' in the resp: " + str(res))

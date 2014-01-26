"""Test the password reset step process


- You've forgotten your password
- You enter your email into the forgotten password ui
    - Your account gets a activation record
    - Your account is deactivated
    - An email with the activation url is emailed to you
- You cannot re-enter the account for activation until the previous one is
  expired/or a successful reset has occurred
- While the account is deactivated you cannot make api calls or view login-only
  urls
- You follow the activation link and can reset your password
- At this point you can log in with the new password
- api and other calls now function

"""
import json
import logging
import transaction

from mock import patch
from pyramid import testing
from unittest import TestCase

from bookie.models import DBSession
from bookie.models.auth import Activation

LOG = logging.getLogger(__name__)


class TestReactivateFunctional(TestCase):

    def _reset_admin(self):
        """Reset the admin account"""
        DBSession.execute(
            "UPDATE users SET activated='1' WHERE username='admin';")
        Activation.query.delete()
        transaction.commit()

    def setUp(self):
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        self._reset_admin()
        testing.tearDown()

    def test_activate_form_bad(self):
        """Test bad call to reset"""
        res = self.testapp.post(
            '/api/v1/suspend',
            content_type='application/json',
            status=406)
        success = json.loads(res.body)['error']
        self.assertTrue(
            success is not None,
            "Should not be successful with no email address: " + str(res))

        res = self.testapp.post('/api/v1/suspend',
                                params={'email': 'notexist@gmail.com'},
                                status=404)
        success = json.loads(res.body)
        self.assertTrue(
            'error' in success,
            "Should not be successful with invalid email address: " + str(res))

    @patch('bookie.lib.message.sendmail')
    def test_activate_form(self, mock_sendmail):
        """ Functional test to see if we can submit the api to reset an account

        Now by doing this we end up marking the account deactivated which
        causes other tests to 403 it up. Need to reinstate the admin account on
        tearDown

        """
        res = self.testapp.post('/api/v1/suspend',
                                params={'email': u'testing@dummy.com'},
                                status=200)

        success = json.loads(res.body)
        self.assertTrue(
            'message' in success,
            "Should be successful with admin email address: " + str(res))
        self.assertTrue(mock_sendmail.called)

    @patch('bookie.lib.message.sendmail')
    def test_activate_form_dual(self, mock_sendmail):
        """Test that we can't resubmit for reset, get prompted to email

        If we reset and then try to say "I've forgotten" a second time, we
        should get a nice message. And that message should allow us to get a
        second copy of the email sent.

        """
        res = self.testapp.post('/api/v1/suspend',
                                params={'email': u'testing@dummy.com'},
                                status=200)
        self.assertTrue(mock_sendmail.called)

        success = json.loads(res.body)
        self.assertTrue(
            'message' in success,
            "Should be successful with admin email address")

        res = self.testapp.post('/api/v1/suspend',
                                params={'email': u'testing@dummy.com'},
                                status=406)

        success = json.loads(res.body)
        self.assertTrue(
            'error' in success,
            "Should not be successful on second try: " + str(res))

        self.assertTrue(
            'already' in str(res),
            "Should find 'already' in the response: " + str(res))

    @patch('bookie.lib.message.sendmail')
    def test_reactivate_process(self, mock_sendmail):
        """Walk through all of the steps at a time

        - First we mark that we've forgotten
        - Then use make sure we get a 403 accessing something
        - Then we go back through our activation using our code
        - Finally verify we can access the earlier item

        """
        res = self.testapp.post('/api/v1/suspend',
                                params={'email': u'testing@dummy.com'},
                                status=200)
        self.assertTrue(mock_sendmail.called)

        success = json.loads(res.body)
        self.assertTrue(
            'message' in success,
            "Should be successful with admin email address")

        # now let's try to login
        # the migrations add a default admin account
        user_data = {'login': 'admin',
                     'password': 'admin',
                     'form.submitted': 'true'}

        res = self.testapp.post('/login',
                                params=user_data,
                                status=200)

        self.assertTrue(
            'account deactivated' in str(res),
            "Login should have failed since we're not active: " + str(res))

        act = Activation.query.first()
        self.testapp.delete(
            "/api/v1/suspend?username={0}&code={1}&password={2}".format(
                user_data['login'],
                act.code,
                'admin'),
            status=200)

        self.assertTrue(
            'activated' in str(res),
            "Should be prompted to login now: " + str(res))

        user_data = {'login': 'admin',
                     'password': 'admin',
                     'form.submitted': 'true'}

        res = self.testapp.post('/login',
                                params=user_data,
                                status=302)

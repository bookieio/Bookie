
import transaction

from bookie.tests import factory
from bookie.tests import TestViewBase


class TestSocialOauthView(TestViewBase):
    """Check if SocialConnections API returns all the added accounts"""

    def test_credentials_duplicate(self):
        """Test if oauth duplicate credentials are allowed """
        message = "Invalid credentials"
        twitter_con = factory.make_twitter_connection()
        key = twitter_con.access_key
        secret = twitter_con.access_secret
        transaction.commit()
        # mock create_twitter_userapi
        self._login_admin()
        res = self.app.get('/oauth/twitter_connect',
                           params={
                               'oauth_token': key,
                               'oauth_verifier': secret
                           },
                           status=200)
        self.assertTrue(
            message in res.body,
            "when same credentials are used backend should show message")

    def test_denied(self):
        """Verify that if the request is denied, we show an error."""
        self._login_admin()
        res = self.app.get('/oauth/twitter_connect',
                           params={
                               'denied': True
                           },
                           status=200)
        error_msg = 'Connection Denied'
        self.assertTrue(
            error_msg in res.body,
            'Denied message displayed to the user.')

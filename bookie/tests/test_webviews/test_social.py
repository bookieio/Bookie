
import transaction

from bookie.tests import factory
from bookie.tests import TestViewBase


class TestSocialOauthView(TestViewBase):
    """Check if SocialConnections API returns all the added accounts"""

    def test_credentials_duplicate(self):
        """Test if oauth duplicate credentials are allowed """
        message = """Another user (Admin) has already connected\
             with those Twitter credentials."""
        factory.make_twitter_connection()
        transaction.commit()
        # mock create_twitter_userapi
        self._login_admin()
        res = self.app.get('/oauth/twitter_connect',
                           status=200)
        self.assertTrue(
            message in res.body,
            "when same credentials are used backend should show message")

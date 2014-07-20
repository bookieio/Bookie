
from unittest import TestCase


class TestSocialOAuth(TestCase):

    def setUp(self):
        """Setup Tests"""
        pass

    def tearDown(self):
        """Tear down each test"""
        pass

    def test_create_twitter_userapi(self):
        """Test if correct urls are rendered if OAuthHandler is edited"""
        # mock create_twitter_OAuthHandler
        self._login_admin()
        res = self.app.get('/oauth/twitter_connect')
        self.assertTrue(
            "https://twitter_url/" in res.body,
            msg="OAuth should render url returned by\
             OAuthHandler when no params")

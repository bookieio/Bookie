
import json
import transaction

from bookie.tests import factory
from bookie.tests import TestViewBase


class TestSocialConnectionsApi(TestViewBase):
    """Check if SocialConnections API returns all the added accounts"""

    def testBaseApi(self):
        factory.make_twitter_connection()
        transaction.commit()

        params = {
            'api_key': self.api_key
        }
        res = self.app.get('/api/v1/admin/social_connections',
                           params=params,
                           status=200)
        connections = json.loads(res.body)
        self.assertEqual('admin',
                         connections['social_connections'][0]['username'],
                         'Username should be admin')

    def testSocialAuthentication(self):
        """Test to check that user login is required to do this api call"""

        res = self.app.get('/api/v1/admin/social_connections',
                           status=403)
        self.assertEqual(
            res.status, "403 Forbidden",
            "status should be 403")

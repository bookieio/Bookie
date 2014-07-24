
from datetime import datetime

from bookie.models.social import SocialMgr
from bookie.tests import TestDBBase


class TestSocialMgr(TestDBBase):

    def testConnectionsStore(self):
        credentials = {
            'is_active': True,
            'last_connection': datetime.now(),
            'uid': "1234",
            'access_key': "dummy",
            'access_secret': "dummy",
            'twitter_username': "admin",
            'refresh_date': datetime.now()}

        SocialMgr.store_twitter_connection('admin', credentials)

        connection = SocialMgr.get_all_connections('admin')
        self.assertEqual(1, len(connection.all()),)

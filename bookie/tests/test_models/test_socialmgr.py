
from datetime import datetime
from pyramid import testing
import transaction
from unittest import TestCase

from bookie.models.social import SocialMgr
from bookie.tests import (
    factory,
    empty_db)


class TestSocialMgr(TestCase):

    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()
        empty_db()

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
        self.assertEqual(1, len(connection.all()))

    def testConnectionsReturn(self):
        factory.make_twitter_connection()
        factory.make_twitter_connection(username='bookie')
        transaction.commit()

        connections = SocialMgr.get_twitter_connections()
        self.assertEqual(2, len(connections))

        connection = SocialMgr.get_twitter_connections('bookie')
        self.assertEqual(1, len(connection))

    def testTweetIdUpdate(self):
        factory.make_twitter_connection(username='admin')
        transaction.commit()

        connections = SocialMgr.get_twitter_connections('admin')
        SocialMgr.update_last_tweet_data(connections[0], '123456')

        new_connections = SocialMgr.get_twitter_connections('admin')
        self.assertEqual(new_connections[0].last_tweet_seen, '123456')

from mock import patch
from datetime import datetime
from datetime import timedelta
import transaction

from bookie.bcelery import tasks
from bookie.models import Bmark
from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import stats
from bookie.models.auth import User
from bookie.models.auth import (
    UserMgr,
    Activation,
)
from bookie.models.stats import StatBookmark

from bookie.tests import empty_db
from bookie.tests import factory
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase


class BCeleryTaskTest(TestDBBase):
    """ Test the celery task runner """

    def setUp(self):
        """Populate the DB with a couple of testing records"""
        trans = transaction.begin()
        user = User()
        user.username = gen_random_word(10)
        self.username = user.username
        DBSession.add(user)

        for i in range(3):
            url = gen_random_word(12)
            b = self.__create_bookmark(url, user.username)
            DBSession.add(b)

        # add bookmark with duplicate url
        new_user = User()
        new_user.username = gen_random_word(10)
        self.new_username = new_user.username
        DBSession.add(new_user)

        b = self.__create_bookmark(url, new_user.username)
        DBSession.add(b)

        trans.commit()

    def __create_bookmark(self, url, username):
        """Helper that creates a bookmark object with a random tag"""
        b = Bmark(
            url=url,
            username=username,
            is_private=False
        )
        tagname = gen_random_word(5)
        b.tags[tagname] = Tag(tagname)
        return b

    def tearDown(self):
        """clear out all the testing DB data"""
        empty_db()

    def test_task_unique_total(self):
        """The task should generate a unique count stat record"""
        # from bookie.bcelery import tasks
        tasks.count_unique()

        stat = StatBookmark.query.first()
        self.assertEqual(stat.attrib, stats.UNIQUE_CT)
        self.assertEqual(stat.data, 3)

    def test_task_count_total(self):
        """The task should generate a total count stat record"""
        tasks.count_total()

        stat = StatBookmark.query.first()
        self.assertEqual(stat.attrib, stats.TOTAL_CT)
        self.assertEqual(stat.data, 4)

    def test_task_count_tags(self):
        """The task should generate a tag count stat record"""
        tasks.count_tags()

        stat = StatBookmark.query.first()
        self.assertEqual(stat.attrib, stats.TAG_CT)
        self.assertEqual(stat.data, 4)

    def test_task_count_user_total(self):
        """The task should generate a total count stat record of a user"""
        tasks.count_total_each_user()

        stats = StatBookmark.query.all()

        expected = {
            'admin': 0,
            self.username: 4,
            self.new_username: 3,
        }

        for stat in stats:
            user_key = stat.attrib.split('_')
            username = user_key[2]
            self.assertTrue(username in expected)
            self.assertEqual(expected[username], stat.data)

    @patch('bookie.bcelery.tasks.create_twitter_api')
    def test_process_twitter_connections(self, mock_create_twitter_api):
        """test if create_twitter_api is called"""
        tasks.process_twitter_connections()
        self.assertFalse(mock_create_twitter_api.called)

        factory.make_twitter_connection()

        tasks.process_twitter_connections()
        self.assertTrue(mock_create_twitter_api.called)

    def test_task_delete_non_activated_account(self):
        """The task should delete non activated users"""
        email = u'testingdelete@gmail.com'
        new_user = UserMgr.signup_user(email, u'testcase')
        users = User.query.all()
        activations = Activation.query.all()
        self.assertEqual(
            4,
            len(users),
            'We should have a total of 4 users : ' + str(len(users))
        )
        self.assertEqual(
            3,
            len(activations),
            'We should have a total of 3 activations: ' + str(len(activations))
        )
        new_user.activation.valid_until = datetime.utcnow()-timedelta(days=35)
        tasks.delete_non_activated_account()
        users = User.query.all()
        activations = Activation.query.all()
        self.assertEqual(
            3,
            len(users),
            'We should have a total of 3 users : ' + str(len(users))
        )
        self.assertEqual(
            2,
            len(activations),
            'We should have a total of 2 activations: ' + str(len(activations))
        )

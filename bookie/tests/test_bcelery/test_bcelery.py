import transaction

from bookie.bcelery import tasks
from bookie.models import Bmark
from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import stats
from bookie.models.auth import User
from bookie.models.stats import StatBookmark

from bookie.tests import empty_db
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
        self.new_username = gen_random_word(10)
        b = self.__create_bookmark(url, self.new_username)
        DBSession.add(b)

        trans.commit()

    def __create_bookmark(self, url, username):
        """Helper that creates a bookmark object with a random tag"""
        b = Bmark(
            url=url,
            username=username
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

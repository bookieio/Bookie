import ConfigParser
import os
import random
import shutil
import transaction
import unittest

from pyramid.config import Configurator
from pyramid import testing

# tools we use to empty tables
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Readable
from bookie.models import Tag, bmarks_tags
from bookie.models.queue import ImportQueue

global_config = {}

ini = ConfigParser.ConfigParser()

# we need to pull the right ini for the test we want to run
# by default pullup test.ini, but we might want to test mysql, pgsql, etc
test_ini = os.environ.get('BOOKIE_TEST_INI', None)
if not test_ini:
    test_ini = 'test.ini'

ini.read(test_ini)
settings = dict(ini.items('app:main'))

BOOKIE_TEST_INI = test_ini
print "USING TEST INI: ", BOOKIE_TEST_INI

# clean up whoosh index between test runs
whoosh_idx = settings['fulltext.index']
try:
    # if this is a sqlite db then try to take care of the db file
    shutil.rmtree(whoosh_idx)
except:
    pass


def gen_random_word(wordLen):
    word = ''
    for i in xrange(wordLen):
        word += random.choice(('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrs'
                               'tuvwxyz0123456789/&='))
    return word


class TestDBBase(unittest.TestCase):
    def setUp(self):
        """Setup Tests"""
        testing.setUp()
        self.trans = transaction.begin()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        self.trans.abort()


class TestViewBase(unittest.TestCase):
    """In setup, bootstrap the app and make sure we clean up after ourselves

    """
    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'main')
        from webtest import TestApp
        self.app = TestApp(app)
        testing.setUp()
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").\
            fetchone()
        self.api_key = res['api_key']

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        session = DBSession()

        # clear things out please
        Bmark.query.delete()
        Tag.query.delete()
        Hashed.query.delete()
        Readable.query.delete()
        ImportQueue.query.delete()

        session.execute(bmarks_tags.delete())
        session.flush()
        transaction.commit()



def empty_db():
    """On teardown, remove all the db stuff"""
    Bmark.query.delete()
    Readable.query.delete()
    # we can't remove the toread tag we have from our commands
    Tag.query.delete()
    Hashed.query.delete()

    DBSession.execute(bmarks_tags.delete())
    DBSession.flush()
    transaction.commit()

# unit tests we want to make sure get run
# from bookie.lib.test_tagcommands import *

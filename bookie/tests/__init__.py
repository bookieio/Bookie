import ConfigParser
import logging
import os
import random
import shutil
import transaction
import unittest

from logging.config import fileConfig
from pyramid import testing

# tools we use to empty tables
from bookie.models import bmarks_tags
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Readable
from bookie.models import Tag
from bookie.models.applog import AppLog
from bookie.models.auth import Activation
from bookie.models.auth import User
from bookie.models.queue import ImportQueue
from bookie.models.stats import StatBookmark
from bookie.models.fulltext import _reset_index

global_config = {}

ini = ConfigParser.ConfigParser()

# we need to pull the right ini for the test we want to run
# by default pullup test.ini, but we might want to test mysql, pgsql, etc
test_ini = os.environ.get('BOOKIE_TEST_INI', None)
if not test_ini:
    test_ini = 'test.ini'

ini.read(test_ini)
settings = dict(ini.items('app:bookie'))
# Setup logging to read from the test ini file.
fileConfig(test_ini)
LOG = logging.getLogger(__name__)

# Shut up the transaction logger
transaction._transaction._LOGGER = LOG

BOOKIE_TEST_INI = test_ini
print "\nUSING TEST INI: ", BOOKIE_TEST_INI

# clean up whoosh index between test runs
whoosh_idx = settings['fulltext.index']
try:
    # if this is a sqlite db then try to take care of the db file
    shutil.rmtree(whoosh_idx)
except:
    pass


def gen_random_word(wordLen):
    word = u''
    for i in xrange(wordLen):
        word += random.choice((u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrs'
                               u'tuvwxyz0123456789/&='))
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
        app = get_app(BOOKIE_TEST_INI, 'bookie')
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
        empty_db()

    def _login_admin(self):
        """Make the login call to the app"""
        self.app.post(
            '/login',
            params={
                "login": u"admin",
                "password": u"admin",
                "form.submitted": u"Log In",
            },
            status=302)


def empty_db():
    """On teardown, remove all the db stuff"""
    DBSession.execute(bmarks_tags.delete())
    Readable.query.delete()
    Bmark.query.delete()
    StatBookmark.query.delete()
    Tag.query.delete()
    # we can't remove the toread tag we have from our commands
    Hashed.query.delete()
    ImportQueue.query.delete()
    # Delete the users not admin in the system.
    Activation.query.delete()
    User.query.filter(User.username != u'admin').delete()

    AppLog.query.delete()
    DBSession.flush()
    transaction.commit()

    # Clear the fulltext index as well.
    _reset_index()

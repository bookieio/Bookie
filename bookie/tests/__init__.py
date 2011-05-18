import ConfigParser
import os
import transaction
import unittest

from pyramid.config import Configurator
from pyramid import testing

# tools we use to empty tables
from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Tag, bmarks_tags
from bookie.models import SqliteBmarkFT

global_config = {}

ini = ConfigParser.ConfigParser()

# we need to pull the right ini for the test we want to run
# by default pullup test.ini, but we might want to test mysql, pgsql, etc
test_ini = os.environ.get('BOOKIE_TEST_INI', None)
if not test_ini:
    test_ini = 'test.ini'

ini.read(test_ini)
settings = dict(ini.items('app:bookie'))

BOOKIE_TEST_INI = test_ini

def setup_db(settings):
    """ We need to create the test sqlite database to run our tests against

    If the db exists, remove it
    We're using the SA-Migrations API to create the db and catch it up to the
    latest migration level for testing

    In theory, we could use this API to do version specific testing as well if
    we needed to.

    If we want to run any tests with a fresh db we can call this function

    """
    from migrate.versioning import api as mig
    sa_url = settings['sqlalchemy.url']
    migrate_repository = 'migrations'

    if 'mysql' in sa_url:
        # MYSQL CONFIG
        from sqlalchemy import create_engine
        engine = create_engine(sa_url)

        # # drop any existing data
        all_tables = engine.execute('SHOW TABLES');
        if all_tables.rowcount:
            qry = "`, `".join([res[0] for res in all_tables])
            engine.execute("DROP TABLES `" + qry + '`;')

    elif 'postgres' in sa_url:
        # MYSQL CONFIG
        from sqlalchemy import create_engine
        engine = create_engine(sa_url)

        # # drop any existing data
        all_tables = engine.execute("""SELECT table_name
                                       FROM information_schema.tables
                                       WHERE table_schema = 'public'
        """);

        if all_tables.rowcount:
            qry = ", ".join([res[0] for res in all_tables])
            engine.execute("DROP TABLE " + qry + ';')


    else:
        # we're hackish here since we're going to assume the test db is whatever is
        # after the last slash of the SA url sqlite:///somedb.db
        db_name = sa_url[sa_url.rindex('/') + 1:]
        try:
            # if this is a sqlite db then try to take care of the db file
            os.remove(db_name)
            open(db_name, 'w').close()
        except:
            pass

    mig.version_control(sa_url, migrate_repository)
    mig.upgrade(sa_url, migrate_repository)


setup_db(settings)


def empty_db():
    """On teardown, remove all the db stuff"""

    if BOOKIE_TEST_INI == 'test.ini':
        SqliteBmarkFT.query.delete()
    Bmark.query.delete()
    Tag.query.delete()
    Hashed.query.delete()

    DBSession.execute(bmarks_tags.delete())
    DBSession.flush()
    transaction.commit()


import ConfigParser
import os
import unittest
from pyramid.config import Configurator
from pyramid import testing

global_config = {}

ini = ConfigParser.ConfigParser()
ini.read('test.ini')
settings = dict(ini.items('app:bookie'))


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

    # we're hackish here since we're going to assume the test db is whatever is
    # after the last slash of the SA url sqlite:///somedb.db
    db_name = sa_url[sa_url.rindex('/') + 1:]
    try:
        os.remove(db_name)
    except:
        pass

    open(db_name, 'w').close()

    mig.version_control(sa_url, migrate_repository)
    mig.upgrade(sa_url, migrate_repository)


setup_db(settings)

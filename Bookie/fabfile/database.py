"""Database Related Fabric Commands"""
from fabric.api import local, require, env
from utils import parse_ini

def sample():
    """Sample environment

    This is just a sample environment used for the require messages below. Your
    real environments should be in the environments.py file

    """
    pass


# DB Migrations
def db_init():
    """ Initiate the versioning of the db.

    :Requires: prerun a environment setting function such as sample/prod

    ::

        $ fab prod db_setup

    """
    require("hosts", provided_by=[sample])
    require("ini", provided_by=[sample])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local("migrate version_control --url={0} --repository={1}".format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations'))


def db_add(desc):
    """Call: fab db_add:'Some New Change'

    :param desc: the text string to identify the migrate file

    ::

        $ fab db_add:"Initial Table Setup"

    """
    require("hosts", provided_by=[sample])
    require("ini", provided_by=[sample])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate script --url={0} --repository={1} "{2}"'.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',
        desc,))


def db_test():
    """Test a new migration against the database:

    :WARNING: could fubar db so only use on test db

    :Requires: prerun a environment setting function such as sample/prod

    To test on the sample server
    ::

        $ fab sample db_test

    """
    require("hosts", provided_by=[sample])
    require("ini", provided_by=[sample])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate test --url={0} --repository={1} '.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',))


def db_upgrade():
    """Upgrade the system to the latest migration available

    :Requires: prerun a environment setting function such as sample/prod

    To upgrade migrations on the sample server
    ::

        $ fab sample db_upgrade

    """
    require("hosts", provided_by=[sample])
    require("ini", provided_by=[sample])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate upgrade --url={0} --repository={1} '.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',))


def db_downgrade(db_version):
    """Downgrade the database system to the specified migration

    :param db_version: the specific migration integer to downgrade t

    :Requires: prerun a environment setting function such as sample/prod

    To upgrade migrations on the sample server
    ::

        $ fab sample db_downgrade:12

    """
    require('hosts', provided_by=[sample])
    require('ini', provided_by=[sample])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate downgrade --url={0} --repository={1} {2} '.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',
        db_version,))

def db_new_install():
    """Initial setup of a db, runs init/upgrade

    :Requires: prerun a environment setting function such as sample/prod

    """
    require('hosts', provided_by=[sample])
    require('ini', provided_by=[sample])

    db_init()
    db_upgrade()

    # we want to provide one default bookmark to start out with
    db_init_bookmark()

def db_init_bookmark():
    """install the initial bookmark in a new install"""
    require('hosts', provided_by=[sample])
    require('ini', provided_by=[sample])

    parse_ini(env["ini_file"])
    from datetime import datetime
    import transaction
    from bookie.models import initialize_sql
    from sqlalchemy import create_engine

    engine = create_engine(env.ini.get('app:bookie', 'sqlalchemy.url'))
    initialize_sql(engine)

    from bookie.models import DBSession
    from bookie.models import Bmark

    bmark_us = Bmark('http://bmark.us',
                     desc="Bookie Website",
                     ext= "Bookie Documentation Home",
                     tags = "bookmarks")

    bmark_us.stored = datetime.now()
    bmark_us.updated = datetime.now()
    DBSession.add(bmark_us)
    DBSession.flush()
    transaction.commit()

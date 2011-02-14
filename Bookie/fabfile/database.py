"""Database Related Fabric Commands"""
from fabric.api import local, require, env
from environments import dev
from utils import parse_ini

# DB Migrations
def db_init():
    """ Initiate the versioning of the db.

    :Requires: prerun a environment setting function such as dev/prod

    ::

        $ fab prod db_setup

    """
    require("hosts", provided_by=[dev])
    require("ini", provided_by=[dev])

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
    require("hosts", provided_by=[dev])
    require("ini", provided_by=[dev])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate script --url={0} --repository={1} "{2}"'.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',
        desc,))


def db_test():
    """Test a new migration against the database:

    :WARNING: could fubar db so only use on test db

    :Requires: prerun a environment setting function such as dev/prod

    To test on the dev server
    ::

        $ fab dev db_test

    """
    require("hosts", provided_by=[dev])
    require("ini", provided_by=[dev])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate test --url={0} --repository={1} '.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',))


def db_upgrade():
    """Upgrade the system to the latest migration available

    :Requires: prerun a environment setting function such as dev/prod

    To upgrade migrations on the dev server
    ::

        $ fab dev db_upgrade

    """
    require("hosts", provided_by=[dev])
    require("ini", provided_by=[dev])

    # load up the ini for this environment
    parse_ini(env["ini_file"])

    local('migrate upgrade --url={0} --repository={1} '.format(
        env.ini.get('app:bookie', 'sqlalchemy.url'),
        'migrations',))

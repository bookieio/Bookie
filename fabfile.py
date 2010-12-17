from fabric.api import run, sudo, hosts, local, cd, env, require, prompt
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm
import os
import subprocess

""" SAMPLE fabfile.py for getting started

"""
# Globals
env.project_name = 'bookie'

docs_host = 'webint'
docs_location = '/var/www/html/sphinx/{project_name}'.format(**env)

# if we want out build script to auto ask us to update the version string in our
# app use these two parameters to open those files so we can update them
env.default_editor = os.environ['EDITOR'] or 'vi'
env.new_version_files = ['{project_name}/__init__.py'.format(**env),
                    'docs/conf.py',
                    ]

if 'EDITOR' in os.environ:
    env.default_editor = os.environ['EDITOR']
else:
    env.default_editor = 'vim'

env.packagedir = 'http://sd2.morpace-i.com/packages/'

# Environments
def prod():
    """Copy settings from dev() and adjust for production"""
    pass

def dev():
    "Use the production server environment settings"
    env.hosts = ['localhost',]
    env.user = 'rharding'
    env.venv_path = '/home/rharding/src/quipp/quippdemo_ve'
    env.app_path = '{venv_path}/{project_name}'.format(**env)
    env.python_path = '{venv_path}/bin/python'.format(**env)
    env.pip_path = '{venv_path}/bin/pip'.format(**env)
    env.nosetests_path = '{venv_path}/bin/nosetests'.format(**env)
    env.migrate_path = '%(python_path)s %(app_path)s/samigrate.py' % env


def build_docs(clean='no', browse='no'):
    """ Generate the Sphinx documentation."""
    c = ""
    if clean.lower() in ['yes', 'y']:
        c = "clean "

    b = ""
    if browse.lower() in ['yes', 'y']:
        b = " && open _build/html/index.html"
    local('cd docs; make {0}html{1}'.format(c, b), capture=False)

@hosts(docs_host)
def push_docs():
    """ Build and push the Sphinx docs to webint.morpace-i.com/sphinx/$project """
    build_docs(clean='yes')
    rsync_project(docs_location, 'docs/_build/html/', delete=True)

# PIP/requirements
def pip_req_refresh():
    """Recreate the requirements.txt file based on the virtualenv pkgs"""
    require('hosts', provided_by=[dev,prod])
    require('app_path', provided_by=[dev,prod])

    file_path = os.path.join(env['app_path'], 'requirements.txt')

    # run pip freeze and nab the output of the command
    pkg_list = subprocess.Popen([env['pip_path'], '-E', env['venv_path'], 'freeze'],
            stdout=subprocess.PIPE).communicate()[0].strip()

    outfile = open(file_path, 'w')
    outfile.write("-f {0}\n".format(env['packagedir']))
    for l in pkg_list:
        outfile.write(l)

@hosts('localhost')
def pip_add():
    """Allow the user to add/edit pip requirements.txt

    Make sure you have $EDITOR defined for your user

    """

    dev()
    local('{0} {app_path}/{1}'.format(env.default_editor,
            'requirements.txt',
            **env),
        capture=False)

    # once the edit is done, let's perform installs
    _pip_require()

    # and after the install, let's regenerate the requirements.txt with the new
    # version strings put in place for us
    pip_req_refresh()


def _pip_require():
    """Run the pip install -r requirements.txt file

    :Requires: prerun a environment setting function such as dev/prod

    To update the packages on the production server run:
    ::

        $ fab prod pip_require

    """
    require('hosts', provided_by=[dev,prod])
    require('app_path', provided_by=[dev,prod])
    run('cd {app_path}; {pip_path} install -r requirements.txt'.format(**env))

# UNIT TESTING
def test():
    "Run the test suite locally. Much faster local vs run so separate function"
    local('nosetests {project_name}/tests'.format(**env), capture=False)

# DB Migrations
def db_setup():
    """ Initiate the versioning of the db.

    :Requires: prerun a environment setting function such as dev/prod

    ::

        $ fab prod db_setup

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        run('{migrate_path} version_control'.format(**env))


def db_version():
    """ Return the current version of the migrations

    :Requires: prerun a environment setting function such as dev/prod

    To get the db migrations version available on production
    ::

        $ fab prod db_version

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        run('{migrate_path} version'.format(**env))

def db_version_db():
    """Return the current migrations version the application is running

    :Requires: prerun a environment setting function such as dev/prod

    To get the db migrations version the prod app is running
    ::

        $ fab prod db_version_db

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        run('{migrate_path} db_version'.format(**env))

def db_add(desc):
    """Call: fab db_add:'Some New Change'

    :param desc: the text string to identify the migrate file

    ::

        $ fab db_add:"Initial Table Setup"

    """
    dev()
    env.new_migration = desc
    local('{migrate_path} script "{new_migration}"'.format(**env))

def db_test():
    """Test a new migration against the database:

    :WARNING: could fubar db so only use on test db

    :Requires: prerun a environment setting function such as dev/prod

    To test on the dev server
    ::

        $ fab dev db_test

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        run('{migrate_path} test'.format(**env))

def db_upgrade():
    """Upgrade the system to the latest migration available

    :Requires: prerun a environment setting function such as dev/prod

    To upgrade migrations on the dev server
    ::

        $ fab dev db_upgrade

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        run('{migrate_path} upgrade'.format(**env))

def db_downgrade(db_version):
    """Downgrade the database system to the specified migration

    :param db_version: the specific migration integer to downgrade to

    :Requires: prerun a environment setting function such as dev/prod

    To upgrade migrations on the dev server
    ::

        $ fab dev db_downgrade:12

    """
    require('hosts', provided_by=[dev,prod])
    require('migrate_path', provided_by=[dev,prod])

    with cd(env.app_path):
        env.db_version = db_version
        run('{migrate_path} downgrade {db_version}'.format(**env))



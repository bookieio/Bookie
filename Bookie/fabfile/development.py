"""Fabric commands useful for working on developing Bookie are loaded here"""
import os

from fabric.api import hosts
from fabric.api import local
from fabric.contrib.project import rsync_project

bootstrap_host = 'ubuntu@bmark'
bootstrap_server = '/var/www/bootstrap.py'
bootstrap_local = 'scripts/bootstrap/bootstrap.py'


def gen_bootstrap():
    """Run the generator that builds a custom virtualenv bootstrap file"""
    local('python scripts/bootstrap/gen_bootstrap.py > scripts/bootstrap/bootstrap.py', capture=False)


@hosts(bootstrap_host)
def push_bootstrap():
    """Sync the bootstrap.py up to the server for download"""
    rsync_project(bootstrap_server, bootstrap_local)

def jstest():
    """Launch the JS tests we have in the system

    Currently only the ones there are for extensions

    """
    cwd = os.path.dirname(os.path.dirname(__file__))
    local('google-chrome {0}/extensions/tests/index.html'.format(cwd))

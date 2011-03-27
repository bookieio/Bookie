"""Fabric commands useful for working on developing Bookie are loaded here"""
import os

from fabric.api import hosts
from fabric.api import local
from fabric.contrib.project import rsync_project

upload_host = 'ubuntu@bmark'
bootstrap_server = '/var/www/bootstrap.py'
bootstrap_local = 'scripts/bootstrap/bootstrap.py'

chrome_bin = '/usr/bin/google-chrome'
chrome_path = 'extensions/chrome_ext'
key = "/home/rharding/.ssh/chrome_ext.pem"
chrome_ext_server = '/var/www/bookie_chrome.crx'
chrome_ext_local = 'extensions/chrome_ext.crx'


def gen_bootstrap():
    """Run the generator that builds a custom virtualenv bootstrap file"""
    local('python scripts/bootstrap/gen_bootstrap.py > scripts/bootstrap/bootstrap.py', capture=False)


@hosts(upload_host)
def push_bootstrap():
    """Sync the bootstrap.py up to the server for download"""
    rsync_project(bootstrap_server, bootstrap_local)

def jstest():
    """Launch the JS tests we have in the system

    Currently only the ones there are for extensions

    """
    cwd = os.path.dirname(os.path.dirname(__file__))
    local('cd {0}/extensions/tests/ && google-chrome index.html'.format(cwd))

def build_chrome_ext():
    """Package the chrome extension into a .crx file"""
    local('{0} --pack-extension={1} --pack-extension-key={2}'.format(chrome_bin,
                                                                    chrome_path,
                                                                    key))
@hosts(upload_host)
def push_chrome_ext():
    """Upload the chrome extension to the server"""
    rsync_project(chrome_ext_server, chrome_ext_local)

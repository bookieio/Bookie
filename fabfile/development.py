"""Fabric commands useful for working on developing Bookie are loaded here"""
from fabric.api import hosts
from fabric.api import local
from fabric.contrib.project import rsync_project

upload_host = 'rharding@dc'
bootstrap_server = '/home/bmark.us/www/'
bootstrap_local = 'scripts/bootstrap/bootstrap.py'

chrome_bin = '/usr/bin/google-chrome'
chrome_path = 'extensions/chrome_ext'
key = "/home/rharding/.ssh/chrome_ext.pem"
chrome_ext_server = '/home/bmark.us/www/bookie_chrome.crx'
chrome_ext_local = 'extensions/chrome_ext.crx'


def gen_bootstrap():
    """Run the generator that builds a custom virtualenv bootstrap file"""
    local('python scripts/bootstrap/gen_bootstrap.py > scripts/bootstrap/bootstrap.py', capture=False)


@hosts(upload_host)
def push_bootstrap():
    """Sync the bootstrap.py up to the server for download"""
    rsync_project(bootstrap_server, bootstrap_local)


def build_chrome_ext():
    """Package the chrome extension into a .crx file"""
    local('{0} --pack-extension={1} --pack-extension-key={2}'.format(chrome_bin,
                                                                    chrome_path,
                                                                    key))
    local('rm chrome_ext.zip && cd extensions/chrome_ext && zip -r ../../chrome_ext.zip .')


def build_ff_ext():
    """Package the firefox extension into a .xpi file"""
    local('rm bookie.xpi && cd extensions/firefox_ext && zip -r ../../bookie.xpi .')


@hosts(upload_host)
@hosts(upload_host)
def push_chrome_ext():
    """Upload the chrome extension to the server"""
    rsync_project(chrome_ext_server, chrome_ext_local)

"""Fabric commands to help add new users to the system"""
from convoy.meta import main
from fabric.api import env, local
from utils import parse_ini

BUILD_JS = 'bookie/static/js/build'
BOOKIE_JS = 'bookie/static/js/bookie'
YUIGITBRANCH = "git://github.com/yui/yui3.git"
TEMPDIR = "/tmp/yui"


def build_js():
    build_metadata()
    build_bookie()
    build_yui()


def build_bookie():
    """Copy over the bookie related JS files to the build dir"""
    local('cp {0}/y*.js {1}/bookie'.format(BOOKIE_JS, BUILD_JS))


def build_metadata():
    """Generate the YUI compatible module list for our application JS"""
    meta_build = "scripts/js/generate_meta.py"
    cmd = "{0} -n YUI_MODULES -s {1} -o {2}/bookie/meta.js"
    local(cmd.format(meta_build, BOOKIE_JS, BUILD_JS))


def build_yui():
    """Add the YUI library over to the build directory"""
    #!/bin/sh
    local('mkdir {0}'.format(TEMPDIR))
    local('git clone --depth 1 {0} {1}'.format(YUIGITBRANCH, TEMPDIR))
    local('cp -r {0}/build {1}/yui'.format(TEMPDIR, BUILD_JS))
    local('rm -rf {0}'.format(TEMPDIR))

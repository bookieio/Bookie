import os
from os.path import dirname
from shutil import copyfile
import sys

from fabric.api import run, sudo, hosts, local, cd, env, require, prompt
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.python_path = sys.executable
env.pip_path = os.path.join(os.path.dirname(env.python_path), 'pip')

env.project_name = "bookie"

env.new_version_files = ["{project_name}/__init__.py".format(**env),
                         "docs/conf.py",
                         "setup.py", ]

# IMPORT the rest of the commands we have available to us
from docs import *
from database import *
from development import *

try:
    from environments import *
except:
    print "No environment currently found, please do: fab new_install:$myinstall"

from tests import *

# starter helpers
def new_install(install_name):
    """For a new install, create a new config file and write it out for them"""
    env_header = """from fabric.api import env"""

    new_env = """


def {0}():
    \"\"\"Environment settings for the dev environment\"\"\"
    env.hosts = ['localhost']
    env.ini_file = "{0}.ini"
    env.ini = None
"""

    environment_file = os.path.join(dirname(__file__), 'environments.py')

    if os.path.exists(environment_file):
        # first check if we already have this defined
        with open(environment_file) as env_file:
            current_env = env_file.read()

        if 'def {0}'.format(install_name) in current_env:
            raise Exception("That install is already defined in environments.py")

        with open(environment_file, 'a') as en_file:
            en_file.write(new_env.format(install_name))

    else:

        with open(environment_file, 'w') as en_file:
            en_file.write(env_header)
            en_file.write(new_env.format(install_name))

    # we also need to create a .ini file for this install
    ini_filename = os.path.join(dirname(dirname(__file__)),
                                "{0}.ini".format(install_name))
    if os.path.exists(ini_filename):
        # then we already have it, don't mess with it
        print "Ini file already exists, skipping creation"
    else:
        sample_filename = os.path.join(dirname(__file__), "sample.ini")

        # need to cp the sample file over as the new ini_filename
        copyfile(sample_filename, ini_filename)

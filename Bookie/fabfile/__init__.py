import os
from os.path import dirname
from shutil import copyfile

from fabric.api import run, sudo, hosts, local, cd, env, require, prompt
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.project_name = "bookie"
env.new_version_files = ["{project_name}/__init__.py".format(**env),
                         "docs/conf.py",
                         "setup.py", ]

# IMPORT the rest of the commands we have available to us
from docs import *
from database import *
from development import *
from environments import *
from tests import *

# starter helpers
def new_install(install_name):
    """For a new install, create a new config file and write it out for them"""

    # first check if we already have this defined
    environment_file = os.path.join(dirname(__file__), 'environments.py')

    current_env = open(environment_file).read()

    if 'def {0}'.format(install_name) in current_env:
        raise Exception("That install is already defined in environments.py")

    new_env = """
def {0}():
    \"\"\"Environment settings for the dev environment\"\"\"
    env.hosts = ['localhost']
    env.ini_file = "{0}.ini"
    env.ini = None

"""

    with open(environment_file, 'a+') as en_file:
        en_file.write(new_env.format(install_name))

    # we also need to create a .ini file for this install
    ini_filename = os.path.join(dirname(dirname(__file__)),
                                "{0}.ini".format(install_name))
    sample_filename = os.path.join(dirname(__file__), "sample.ini")

    # need to cp the sample file over as the new ini_filename
    copyfile(sample_filename, ini_filename)

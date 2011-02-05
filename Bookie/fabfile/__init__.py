import ConfigParser

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

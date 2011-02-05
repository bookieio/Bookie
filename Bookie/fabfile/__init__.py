from fabric.api import run, sudo, hosts, local, cd, env, require, prompt
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.project_name = 'bookie'

env.new_version_files = ['{project_name}/__init__.py'.format(**env),
                         'docs/conf.py',
                         'setup.py', ]

# @todo need to figure out how to handle host specific settings on a
# distributed/open app like this


def build_docs(clean="no", browse="no"):
    """Run the sphinx build on the docs"""
    if clean.lower() in ['yes', 'y']:
        c_flag = "clean "
    else:
        c_flag = ""

    if browse.lower() in ['yes', 'y']:
        b_flag = " && open _build/html/index.html"
    else:
        b_flag = ""

    local('cd docs; make {0}html{1}'.format(c_flag, b_flag), capture=False)

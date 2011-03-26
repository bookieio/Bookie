from fabric.api import local, hosts
from fabric.contrib.project import rsync_project

docs_host = 'ubuntu@bmark'
docs_location = '/var/www/'

def build_docs(clean="no", browse="no"):
    """Run the sphinx build on the docs"""
    if clean.lower() in ["yes", "y"]:
        c_flag = "clean "
    else:
        c_flag = ""

    if browse.lower() in ["yes", "y"]:
        b_flag = " && open _build/html/index.html"
    else:
        b_flag = ""

    local("cd docs; make {0}html{1}".format(c_flag, b_flag), capture=False)

@hosts(docs_host)
def push_docs():
    """Build and push the docs up to the host"""
    build_docs(clean='yes')
    rsync_project(docs_location, 'docs/_build/html/', delete=True)



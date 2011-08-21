import os
from fabric.api import env, local

# UNIT TESTING
def test():
    "Run the test suite locally. Much faster local vs run so separate function"
    local('nosetests --with-id {project_name}/tests'.format(**env), capture=False)


def jstest():
    """Launch the JS tests we have in the system

    Currently only the ones there are for extensions

    """
    cwd = os.path.dirname(os.path.dirname(__file__))
    local('cd {0}/extensions/tests/ && phantomjs --local-access-remote=yes ptests.js index.html'.format(cwd), capture=False)

def jsview():
    """Run the tests, but save the test output to a test.pdf file we can
    open/monitor

    """
    cwd = os.path.dirname(os.path.dirname(__file__))
    local('cd {0}/extensions/tests/ && phantomjs --local-access-remote=yes prender.js index.html test.pdf && google-chrome test.pdf'.format(cwd), capture=False)

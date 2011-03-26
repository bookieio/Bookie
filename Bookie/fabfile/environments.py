from fabric.api import env
# @todo need to figure out how to handle host specific settings on a
# distributed/open app like this
def dev():
    """Environment settings for the dev environment"""
    env.hosts = ['localhost']
    env.ini_file = "development.ini"
    env.ini = None

def rick():
    """Environment settings for the dev environment"""
    env.hosts = ['localhost']
    env.ini_file = "rick.ini"
    env.ini = None


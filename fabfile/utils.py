import ConfigParser

from fabric.api import env


def parse_ini(path):
    """Generate a ConfigObject instance for env.ini"""
    env.ini = ConfigParser.ConfigParser()
    env.ini.read(path)

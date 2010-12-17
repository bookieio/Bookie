import logging
#logging.basicConfig(level=logging.DEBUG)

__version__ = '0.0.1'

APP_PATH = None
CONFIG_PATH = None
APP_NAME = None
APP_CONF = None
PYLONS_CONF = None

def get_appconfig(with_pylons=False):
    """Allow outside scripts to get application conf information

    Sets the follow constants we can reference once this is run as:
    app_name.APP_PATH
    app_name.CONFIG_PATH
    app_name.APP_NAME
    app_name.APP_CONF

    :return: ConfigParser file active_ini

    """
    global APP_CONF
    global CONFIG_PATH
    global APP_NAME
    global APP_PATH
    global PYLONS_CONF

    # if this is already set just return it
    if APP_CONF:
        return APP_CONF

    import ConfigParser
    import os
    import socket

    # Read the entry for the hostname
    current_host = socket.gethostname().split('.')[0].lower()

    # let's get our app information and paths so we can assume the location of other
    # files
    APP_PATH = os.path.dirname(os.path.abspath(__file__))

    # the ve_dir is the dirname one level up from the app path
    ve_dir = os.path.basename(os.path.dirname(APP_PATH))

    CONFIG_PATH = os.path.dirname(APP_PATH)

    # app name is this package
    APP_NAME = __name__
    log = logging.getLogger(APP_NAME)

    log.debug('Hostname: {0}'.format(current_host))
    log.debug('APP_PATH: {0}'.format(APP_PATH))
    log.debug('CONFIG_PATH: {0}'.format(CONFIG_PATH))
    log.debug('APP_NAME: {0}'.format(APP_NAME))
    log.debug('VE Name: {0}'.format(ve_dir))

    # now let's load up the root.ini to find out what file we're using for our
    # runtime information
    root_ini = ConfigParser.ConfigParser()
    root_ini.read(os.path.join(CONFIG_PATH, "root.ini"))

    # root.ini file is expected to have just the following
    # [pyrite]
    # ini = stage.ini
    # 
    # [dashX]
    # ini = production.ini

    active_ini = ConfigParser.ConfigParser()
    ini_section = "{0}_{1}".format(current_host, ve_dir)
    ini_file = root_ini.get(ini_section, 'ini')
    log.debug('Using ini file: {0}'.format(ini_file))

    active_ini.read(os.path.join(CONFIG_PATH, ini_file))

    if with_pylons:
        ini_path = os.path.join(CONFIG_PATH, ini_file)
        pylons_config = _load_pylons(ini_path)
        PYLONS_CONF = pylons_config

    # set this to the module so that future things can import it/use it
    APP_CONF = active_ini
    return active_ini

def _load_pylons(config_file):
    from paste.deploy import appconfig 
    from pylons import config 
    import ConfigParser 
    import os 
     
    from config.environment import load_environment 
     
    conf = appconfig('config:' + config_file) 
    config = load_environment(conf.global_conf, conf.local_conf)
    return config



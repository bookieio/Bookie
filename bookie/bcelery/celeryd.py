from celery import Celery
from ConfigParser import ConfigParser
from datetime import timedelta
from os import environ
from os import path

import bookie.bcelery

# We import this to be the target of our command line launch.
from bookie.bcelery import celery


def load_ini():
    selected_ini = environ.get('BOOKIE_INI', None)
    if selected_ini is None:
        msg = "Please set the BOOKIE_INI env variable!"
        raise Exception(msg)

    cfg = ConfigParser()
    ini_path = path.join(
        path.dirname(
            path.dirname(
                path.dirname(__file__)
            )
        ),
        selected_ini
    )
    cfg.readfp(open(ini_path))

    # Hold onto the ini config.
    return dict(cfg.items('app:bookie', raw=True))

bookie.bcelery.ini = load_ini()

import bookie.bcelery.tasks

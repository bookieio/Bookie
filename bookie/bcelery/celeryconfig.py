"""Celery config for Bookie Instance"""
import ConfigParser
from datetime import timedelta
from os import environ
from os import path

import tasks

def load_config():
    selected_ini = environ.get('BOOKIE_INI', None)

    if selected_ini is None:
        msg = "Please set the BOOKIE_INI env variable!"
        raise Exception(msg)

    ini = ConfigParser()
    ini_path = path.join(
        path.dirname(
            path.dirname(
                path.dirname(__file__)
            )
        ),
        selected_ini
    )
    ini.readfp(open(ini_path))
    return ini

INI = load_config()

# List of modules to import when celery starts.
CELERY_IMPORTS = ("bookie.bcelery.tasks", )
CELERY_ENABLE_UTC = True


## Result store settings.
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "sqlite:///../../bookie.db"

## Broker settings.
BROKER_TRANSPORT = "sqlalchemy"
BROKER_HOST = "sqlite:///../../bookie.db"
# BROKER_URL = "amqp://guest:guest@localhost:5672//"


## Worker settings
## If you're doing mostly I/O you can have more processes,
## but if mostly spending CPU, try to keep it close to the
## number of CPUs on your machine. If not set, the number of CPUs/cores
## available will be used.
CELERYD_CONCURRENCY = 1

# CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
CELERYBEAT_SCHEDULE = {
    "tasks.hourly_stats": {
        "task": "tasks.hourly_stats",
        "schedule": timedelta(seconds=60 * 60),
    },
    "tasks.importer_depth": {
        "task": "tasks.importer_depth",
        "schedule": timedelta(seconds=60 * 1),
    },
    "tasks.importer": {
        "task": "tasks.importer_process",
        "schedule": timedelta(seconds=60 * 1),
    },
}

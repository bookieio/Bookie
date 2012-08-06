from celery import Celery
from datetime import timedelta
from os import environ
from os import path


def load_config(settings=None):
    import bookie.bcelery
    bookie.bcelery.ini = settings
    # Only import the tasks after we've setup the ini config.
    import bookie.bcelery.tasks

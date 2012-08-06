from celery import Celery


# Override these in each implementation for app and celeryd running.
celery = Celery()
ini = None

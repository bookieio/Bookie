"""Celery config loaded from the Bookie web application side

It's getting the copy of the settings from the Pyramid application bootstrap.

"""


def load_config(settings):
    import bookie.bcelery
    bookie.bcelery.ini = settings
    # Only import the tasks after we've setup the ini config.
    import bookie.bcelery.tasks

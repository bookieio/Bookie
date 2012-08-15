"""mycelery Tasks to perform"""
import celery
import transaction

from datetime import datetime
from datetime import timedelta
from os.path import dirname

import bookie
from bookie.lib.importer import Importer
from bookie.lib.rrdstats import SystemCounts
from bookie.lib.rrdstats import ImportQueueDepth

from bookie.models import initialize_sql
from bookie.models import BmarkMgr
from bookie.models import TagMgr
from bookie.models.stats import StatBookmarkMgr
from bookie.models.queue import ImportQueueMgr

from bookie.bcelery import celery as mycelery
from bookie.bcelery import ini


HERE = dirname(dirname(dirname(__file__)))


if ini is None:
    from bookie.bcelery.celeryd import load_ini
    ini = load_ini()


bookie.bcelery.celery.conf.update(
    # List of modules to import when celery starts.
    CELERY_IMPORTS=("bookie.bcelery.tasks", ),
    CELERY_ENABLE_UTC=True,

    ## Result store settings.
    CELERY_RESULT_BACKEND=ini.get('celery_result_backend'),
    CELERY_RESULT_DBURI=ini.get('celery_result_dburi'),

    ## Broker settings.
    BROKER_TRANSPORT=ini.get('celeryd_broker_transport'),
    BROKER_HOST=ini.get('celery_broker_host'),
    # BROKER_URL = "amqp://guest:guest@localhost:5672//"

    ## Worker settings
    ## If you're doing mostly I/O you can have more processes,
    ## but if mostly spending CPU, try to keep it close to the
    ## number of CPUs on your machine. If not set, the number of CPUs/cores
    ## available will be used.
    CELERYD_CONCURRENCY=ini.get('celery_concurrency'),

    # CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
    CELERYBEAT_SCHEDULE={
        "tasks.hourly_stats": {
            "task": "tasks.hourly_stats",
            "schedule": timedelta(seconds=60 * 60),
        },
        "tasks.stats_rrd": {
            "task": "bookie.bcelery.tasks.generate_count_rrd",
            "schedule": timedelta(seconds=60 * 60 * 12),
        },
        "tasks.importer_depth": {
            "task": "bookie.bcelery.tasks.importer_depth",
            "schedule": timedelta(seconds=60 * 5),
        },
        "tasks.generate_importer_depth_rrd": {
            "task": "bookie.bcelery.tasks.generate_importer_depth_rrd",
            "schedule": timedelta(seconds=60 * 5),
        },
        "tasks.importer": {
            "task": "bookie.bcelery.tasks.importer_process",
            "schedule": timedelta(seconds=60 * 3),
        },
    },
)


@mycelery.task(ignore_result=True)
def hourly_stats():
    """Hourly we want to runa series of numbers to track

    Currently we're monitoring:
    - Total number of bookmarks in the system
    - Unique number of urls in the system
    - Total number of tags in the system

    """
    celery.task.subtask(count_total).delay()
    celery.task.subtask(count_unique).delay()
    celery.task.subtask(count_tags).delay()
    # celery.task.subtask(count_rrd).delay()


@mycelery.task(ignore_result=True)
def count_total():
    """Count the total number of bookmarks in the system"""
    trans = transaction.begin()
    initialize_sql(ini)
    StatBookmarkMgr.count_total_bookmarks()
    trans.commit()


@mycelery.task(ignore_result=True)
def count_unique():
    """Count the unique number of bookmarks/urls in the system"""
    trans = transaction.begin()
    initialize_sql(ini)
    StatBookmarkMgr.count_unique_bookmarks()
    trans.commit()


@mycelery.task(ignore_result=True)
def count_tags():
    """Count the total number of tags in the system"""
    trans = transaction.begin()
    initialize_sql(ini)
    StatBookmarkMgr.count_total_tags()
    trans.commit()


@mycelery.task(ignore_result=True)
def count_rrd():
    """Add these counts to the rrd graph"""
    rrd = SystemCounts(
        ini.get('rrd_data').format(here=HERE),
        ini.get('rrd_graphs').format(here=HERE))
    rrd.mark(
        datetime.now(),
        BmarkMgr.count(),
        BmarkMgr.count(distinct=True),
        TagMgr.count()
    )
    rrd.update()


@mycelery.task(ignore_result=True)
def generate_count_rrd():
    """Update the png for the counts."""
    rrd = SystemCounts(
        ini.get('rrd_data').format(here=HERE),
        ini.get('rrd_graphs').format(here=HERE))
    rrd.output()


@mycelery.task(ignore_result=True)
def importer_depth():
    """Update the RRD data for the import queue depth."""
    trans = transaction.begin()
    initialize_sql(ini)
    StatBookmarkMgr.count_importer_depth()
    trans.commit()
    celery.task.subtask(importer_depth_rrd).delay()


@mycelery.task(ignore_result=True)
def importer_depth_rrd():
    """Add these counts to the rrd graph"""
    rrd = ImportQueueDepth(
        ini.get('rrd_data').format(here=HERE),
        ini.get('rrd_graphs').format(here=HERE))
    rrd.mark(
        datetime.now(),
        ImportQueueMgr.size()
    )
    rrd.update()


@mycelery.task(ignore_result=True)
def generate_importer_depth_rrd():
    """Update the png for the counts."""
    rrd = ImportQueueDepth(
        ini.get('rrd_data').format(here=HERE),
        ini.get('rrd_graphs').format(here=HERE))
    rrd.output()


@mycelery.task(ignore_result=True)
def importer_process():
    """Check for new imports that need to be scheduled to run"""
    initialize_sql(ini)
    imports = ImportQueueMgr.get_ready(limit=1)

    for i in imports:
        # Log that we've scheduled it
        logger = importer_process.get_logger()
        logger.info("IMPORT: SCHEDULED for {username}.".format(**dict(i)))
        # We need to mark that it's running to prevent it getting picked up
        # again.
        trans = transaction.begin()
        i.mark_running()
        trans.commit()
        celery.task.subtask(importer_process_worker, args=(i.id,)).delay()


@mycelery.task(ignore_result=True)
def importer_process_worker(iid):
    """Do the real import work

    :param iid: import id we need to pull and work on

    """
    logger = importer_process_worker.get_logger()

    trans = transaction.begin()
    initialize_sql(ini)
    import_job = ImportQueueMgr.get(iid)
    logger.info("IMPORT: RUNNING for {username}".format(**dict(import_job)))
    try:
        # process the file using the import script
        import_file = open(import_job.file_path)
        importer = Importer(
            import_file,
            import_job.username)
        importer.process()
        import_job.mark_done()
        logger.info(
            "IMPORT: COMPLETE for {username}".format(**dict(import_job)))
    except Exception, exc:
        # we need to log this and probably send an error email to the
        # admin
        logger = importer_process_worker.get_logger()
        logger.error(str(exc))
        import_job.mark_error()
    trans.commit()


@mycelery.task(ignore_result=True)
def email_signup_user(email, msg, settings, message_data):
    """Do the real import work

    :param iid: import id we need to pull and work on

    """
    from bookie.lib.message import InvitationMsg
    msg = InvitationMsg(email, msg, settings)
    status = msg.send(message_data)
    if status == 4:
        from bookie.lib.applog import SignupLog
        trans = transaction.begin()
        initialize_sql(ini)
        SignupLog(SignupLog.ERROR,
                  'Could not send smtp email to signup: ' + email)
        trans.commit()

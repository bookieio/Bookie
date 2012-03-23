"""Celery Tasks to perform"""
import transaction
from celery.task import task
from celery.task import subtask
from ConfigParser import ConfigParser
from os import getcwd
from os import path

from bookie.lib.importer import Importer

from bookie.models import initialize_sql
from bookie.models.stats import StatBookmarkMgr
from bookie.models.queue import ImportQueueMgr


ini = ConfigParser()
ini_path = path.join(
    path.dirname(
        path.dirname(
            path.dirname(__file__)
        )
    ), 'bookie.ini')
ini.readfp(open(ini_path))
# Set the here var so we can use it to get the path for things.
ini.set('app:main', 'here', getcwd())
ini_items = dict(ini.items("app:main"))
importer_processors = 2


@task(ignore_result=True)
def hourly_stats():
    """Hourly we want to runa series of numbers to track

    Currently we're monitoring:
    - Total number of bookmarks in the system
    - Unique number of urls in the system
    - Total number of tags in the system

    """
    subtask(count_total).delay()
    subtask(count_unique).delay()
    subtask(count_tags).delay()


@task(ignore_result=True)
def count_total():
    """Count the total number of bookmarks in the system"""
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_total_bookmarks()
    trans.commit()


@task(ignore_result=True)
def count_unique():
    """Count the unique number of bookmarks/urls in the system"""
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_unique_bookmarks()
    trans.commit()


@task(ignore_result=True)
def count_tags():
    """Count the total number of tags in the system"""
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_total_tags()
    trans.commit()


@task(ignore_result=True)
def importer_depth():
    """Log how deep the import queue is

    The import queue is currently time based, so we want to make sure we
    monitor how deep the queue is at any given time.

    The queue is currently handled via scheduled tasks so if it backs up we
    might want to process it more frequently.

    """
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_importer_depth()
    trans.commit()


@task(ignore_result=True)
def importer_process():
    """Check for new imports that need to be scheduled to run"""
    initialize_sql(ini_items)
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
        subtask(importer_process_worker, args=(i.id,)).delay()


@task(ignore_result=True)
def importer_process_worker(iid):
    """Do the real import work

    :param iid: import id we need to pull and work on

    """
    logger = importer_process_worker.get_logger()

    trans = transaction.begin()
    initialize_sql(ini_items)
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

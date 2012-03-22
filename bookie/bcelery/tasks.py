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
# set the here var so we can use it to get the path for things
ini.set('app:main', 'here', getcwd())

ini_items = dict(ini.items("app:main"))
importer_processors = 2


@task(ignore_result=True)
def hourly_stats():
    subtask(count_total).delay()
    subtask(count_unique).delay()
    subtask(count_tags).delay()


@task(ignore_result=True)
def count_total():
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_total_bookmarks()
    trans.commit()


@task(ignore_result=True)
def count_unique():
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_unique_bookmarks()
    trans.commit()


@task(ignore_result=True)
def count_tags():
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_total_tags()
    trans.commit()


@task(ignore_result=True)
def importer_depth():
    trans = transaction.begin()
    initialize_sql(ini_items)
    StatBookmarkMgr.count_importer_depth()
    trans.commit()


@task(ignore_result=True)
def importer_process():
    trans = transaction.begin()
    initialize_sql(ini_items)
    imports = ImportQueueMgr.get_ready(limit=1)

    for i in imports:
        subtask(importer_process_worker, args=(i.id,)).delay()

    trans.commit()


@task(ignore_result=True)
def importer_process_worker(iid):
    """Do the real work"""
    trans = transaction.begin()
    initialize_sql(ini_items)
    import_job = ImportQueueMgr.get(iid)
    try:
        # process the file using the import script
        import_job.mark_running()
        import_file = open(import_job.file_path)
        importer = Importer(
            import_file,
            import_job.username)
        importer.process()
        import_job.mark_done()
    except Exception, exc:
        # we need to log this and probably send an error email to the
        # admin
        logger = importer_process_worker.get_logger()
        logger.error(str(exc))
        import_job.mark_error()
    trans.commit()

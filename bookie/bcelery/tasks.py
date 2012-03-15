"""Celery Tasks to perform"""
import transaction
from celery.task import task
from celery.task import subtask
from ConfigParser import ConfigParser
from os import path

from bookie.models import initialize_sql
from bookie.models.stats import StatBookmarkMgr

ini = ConfigParser()
ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), 'bookie.ini')
ini.readfp(open(ini_path))
ini_items = dict(ini.items("app:main"))

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



from __future__ import absolute_import
from celery.utils.log import get_task_logger

from bookie.bcelery.celery import celery


import transaction
from whoosh.store import LockError
from whoosh.writing import IndexingError

from bookie.lib.importer import Importer
from bookie.lib.readable import ReadUrl
from bookie.models import initialize_sql
from bookie.models import Bmark
from bookie.models import BmarkMgr
from bookie.models import Readable
from bookie.models.auth import UserMgr
from bookie.models.stats import StatBookmarkMgr
from bookie.models.queue import ImportQueueMgr

from .celery import load_ini

INI = load_ini()
initialize_sql(INI)

logger = get_task_logger(__name__)


@celery.task(ignore_result=True)
def hourly_stats():
    """Hourly we want to run a series of numbers to track

    Currently we're monitoring:
    - Total number of bookmarks in the system
    - Unique number of urls in the system
    - Total number of tags in the system

    """
    count_total.delay()
    count_unique.delay()
    count_tags.delay()


@celery.task(ignore_result=True)
def daily_stats():
    """Daily we want to run a series of numbers to track

    Currently we're monitoring:
    - Total number of bookmarks for each user in the system

    """
    count_total_each_user.delay()
    delete_non_activated_account.delay()


@celery.task(ignore_result=True)
def delete_non_activated_account():
    """Delete user accounts which are not verified since
    30 days of signup"""
    trans = transaction.begin()
    UserMgr.delete_non_activated_account()
    trans.commit()


@celery.task(ignore_result=True)
def count_total():
    """Count the total number of bookmarks in the system"""
    trans = transaction.begin()
    StatBookmarkMgr.count_total_bookmarks()
    trans.commit()


@celery.task(ignore_result=True)
def count_total_each_user():
    """Count the total number of bookmarks for each user in the system"""
    trans = transaction.begin()
    user_list = UserMgr.get_list(active=True)
    for user in user_list:
        StatBookmarkMgr.count_user_bookmarks(user.username)
    trans.commit()


@celery.task(ignore_result=True)
def count_unique():
    """Count the unique number of bookmarks/urls in the system"""
    trans = transaction.begin()
    StatBookmarkMgr.count_unique_bookmarks()
    trans.commit()


@celery.task(ignore_result=True)
def count_tags():
    """Count the total number of tags in the system"""
    trans = transaction.begin()
    StatBookmarkMgr.count_total_tags()
    trans.commit()


@celery.task(ignore_result=True)
def delete_all_bookmarks(username):
    """ Deletes all bookmarks for the current user"""
    trans = transaction.begin()
    BmarkMgr.delete_all_bookmarks(username)
    trans.commit()


@celery.task()
def importer_process(import_id):
    """Start the process of running the import.

    We load it, mark it as running, and begin begin a task to process.

    :param import_id: import id we need to pull and work on

    """
    trans = transaction.begin()
    imp = ImportQueueMgr.get(import_id)
    import_id = imp.id

    # Log that we've scheduled it
    logger.info("IMPORT: SCHEDULED for {0}.".format(imp.username))
    # We need to mark that it's running to prevent it getting picked up
    # again.
    imp.mark_running()
    trans.commit()
    importer_process_worker.delay(import_id)


@celery.task()
def importer_process_worker(import_id):
    """Do the real import work

    :param import_id: import id we need to pull and work on

    """
    trans = transaction.begin()
    import_job = ImportQueueMgr.get(import_id)
    logger.info("IMPORT: RUNNING for {username}".format(**dict(import_job)))

    try:
        # process the file using the import script
        import_file = open(import_job.file_path)
        importer = Importer(
            import_file,
            import_job.username)
        importer.process()

        # Processing kills off our transaction so we need to start a new one
        # to update that our import is complete.
        trans = transaction.begin()
        import_job = ImportQueueMgr.get(import_id)
        import_job.mark_done()
        user = UserMgr.get(username=import_job.username)
        from bookie.lib.message import UserImportSuccessMessage
        msg = UserImportSuccessMessage(
            user.email,
            'Bookie: Your requested import has completed.',
            INI)
        msg.send({
            'username': import_job.username,
        })

        logger.info(
            "IMPORT: COMPLETE for {username}".format(**dict(import_job)))
        trans.commit()

    except Exception, exc:
        # We need to log this and probably send an error email to the
        # admin
        from bookie.lib.message import ImportFailureMessage
        from bookie.lib.message import UserImportFailureMessage

        trans = transaction.begin()
        import_job = ImportQueueMgr.get(import_id)
        user = UserMgr.get(username=import_job.username)

        msg = ImportFailureMessage(
            INI.get('email.from'),
            'Import failure!',
            INI)
        msg.send({
            'username': import_job.username,
            'file_path': import_job.file_path,
            'exc': str(exc)
        })

        # Also send an email to the user that their import failed.
        msg = UserImportFailureMessage(
            user.email,
            'Bookie: We are sorry, your import failed.',
            INI)
        msg.send({
            'username': import_job.username,
            'exc': str(exc)
        })

        logger.error(exc)
        logger.error(str(exc))
        import_job.mark_error()
        logger.info(
            "IMPORT: ERROR for {username}".format(**dict(import_job)))
        logger.info(exc)
        trans.commit()


@celery.task(ignore_result=True)
def email_signup_user(email, msg, settings, message_data):
    """Do the real import work

    :param iid: import id we need to pull and work on

    """
    from bookie.lib.message import ActivationMsg
    msg = ActivationMsg(email, msg, settings)
    status = msg.send(message_data)
    if status == 4:
        from bookie.lib.applog import SignupLog
        trans = transaction.begin()
        SignupLog(SignupLog.ERROR,
                  'Could not send smtp email to signup: ' + email)
        trans.commit()


class BookmarkNotFoundException(Exception):
    pass


@celery.task(ignore_result=True, default_retry_delay=30)
def fulltext_index_bookmark(bid, content):
    """Insert bookmark data into the fulltext index."""
    b = Bmark.query.get(bid)

    if not b:
        logger.error('Could not load bookmark to fulltext index: ' + str(bid))
        fulltext_index_bookmark.retry(exc=BookmarkNotFoundException())
    else:
        from bookie.models.fulltext import get_writer
        logger.debug('getting writer')
        writer = get_writer()

        if content:
            found_content = content
        elif b.readable:
            found_content = b.readable.clean_content
        else:
            found_content = u""

        try:
            writer.update_document(
                bid=unicode(b.bid),
                description=b.description if b.description else u"",
                extended=b.extended if b.extended else u"",
                tags=b.tag_str if b.tag_str else u"",
                readable=found_content,
            )
            writer.commit()
            logger.debug('writer commit')
        except (IndexingError, LockError), exc:
            # There was an issue saving into the index.
            logger.error(exc)
            logger.warning('sending back to the queue')
            # This should send the work over to a celery task that will try
            # again in that space.
            writer.cancel()
            fulltext_index_bookmark.retry(exc=exc, countdown=60)


@celery.task(ignore_result=True)
def reindex_fulltext_allbookmarks(sync=False):
    """Rebuild the fulltext index with all bookmarks."""
    logger.debug("Starting freshen of fulltext index.")

    bookmarks = Bmark.query.all()

    for b in bookmarks:
        if sync:
            fulltext_index_bookmark(b.bid, None)
        else:
            fulltext_index_bookmark.delay(b.bid, None)


@celery.task(ignore_result=True)
def fetch_unfetched_bmark_content(ignore_result=True):
    """Check the db for any unfetched content. Fetch and index."""
    logger.info("Checking for unfetched bookmarks")

    url_list = Bmark.query.outerjoin(
        Readable, Bmark.readable).\
        filter(Readable.imported.is_(None)).all()

    for bmark in url_list:
        fetch_bmark_content.delay(bmark.bid)


@celery.task(ignore_result=True)
def fetch_bmark_content(bid):
    """Given a bookmark, fetch its content and index it."""
    trans = transaction.begin()

    if not bid:
        raise Exception('missing bookmark id')
    bmark = Bmark.query.get(bid)
    if not bmark:
        raise Exception('Bookmark not found: ' + str(bid))
    hashed = bmark.hashed

    try:
        read = ReadUrl.parse(hashed.url)
    except ValueError:
        # We hit this where urllib2 choked trying to get the protocol type of
        # this url to fetch it.
        logger.error('Could not parse url: ' + hashed.url)
        logger.error('exc')
        read = None

    if read:
        logger.debug(read)
        logger.debug(read.content)

        logger.debug("%s: %s %d %s %s" % (
            hashed.hash_id,
            read.url,
            len(read.content) if read.content else -1,
            read.is_error(),
            read.status_message))

        if not read.is_image():
            if not bmark.readable:
                bmark.readable = Readable()

            bmark.readable.content = read.content
        else:
            if not bmark.readable:
                bmark.readable = Readable()
            bmark.readable.content = None

        # set some of the extra metadata
        bmark.readable.content_type = read.content_type
        bmark.readable.status_code = read.status
        bmark.readable.status_message = read.status_message
        trans.commit()
        fulltext_index_bookmark.delay(
            bid,
            read.content if read else None)
    else:
        logger.error(
            'No readable record for bookmark: ',
            str(bid), str(bmark.hashed.url))

        # There was a failure reading the thing.
        bmark.readable = Readable()
        bmark.readable.status = '900'
        bmark.readable.status_message = (
            'No readable record '
            'during existing processing')
        trans.commit()

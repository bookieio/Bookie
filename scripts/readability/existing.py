"""Run readability on all of the existing urls in the databse


"""
import argparse
import logging
import threading
import time
import transaction

from ConfigParser import ConfigParser
from os import path
from Queue import Queue

from bookie.lib.readable import ReadUrl

from bookie.models import initialize_sql
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Readable

PER_TRANS = 24
LOG = logging.getLogger(__name__)

# Set up some global variables
num_fetch_threads = 8


def parse_args():
    """Parse out the command options. We want to support

    """
    desc = "Update existing bookbmarks with the readability parsed"

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--ini', dest='ini',
                            action='store',
                            default=None,
                            required=True,
                            help='What .ini are we pulling the db connection from?')

    parser.add_argument('--new', dest="new_only",
                        action="store_true",
                        default=False,
                        help="Only parse new bookmarks that have not been attempted before")

    parser.add_argument('--retry-errors', dest="retry_errors",
                        action="store_true",
                        default=False,
                        help="Try to reload content that had an error last time")

    parser.add_argument('--test-url', dest="test_url",
                        action="store",
                        default=False,
                        help="Run the parser on the url provided and test things out")

    args = parser.parse_args()
    return args


def fetch_content(i, q):
    """Our threaded worker to fetch the url contents"""
    while True:
        hash_id, url = q.get()
        print 'Q' + str(i) + ' getting content for ' + hash_id + ' ' + url
        read = ReadUrl.parse(url)
        parsed[hash_id] = read
        q.task_done()


if __name__ == "__main__":
    args = parse_args()

    if args.test_url:
        # then we only want to test this one url and not process full lists
            read = ReadUrl.parse(args.test_url)

            print "META"
            print "*" * 30

            print read.content_type
            print read.status
            print read.status_message

            print "\n\n"

            if not read.is_image():
                print read.content
            else:
                print "Url is an image"

    else:
        # we need to make sure you submitted an ini file to use:
        # args.ini

        ini = ConfigParser()
        ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), args.ini)
        ini.readfp(open(ini_path))

        initialize_sql(dict(ini.items("app:main")))

        ct = 0

        all = False
        while(not all):
            # start the queue up we'll use to thread the url fetching
            enclosure_queue = Queue()

            if args.new_only:
                # we take off the offset because each time we run, we should have
                # new ones to process. The query should return the 10 next
                # non-imported urls
                url_list = Bmark.query.outerjoin(Readable, Bmark.readable).\
                            filter(Readable.imported == None).\
                            limit(PER_TRANS).all()

            elif args.retry_errors:
                # we need a way to handle this query. If we offset and we clear
                # errors along the way, we'll skip potential retries
                # but if we don't we'll just keep getting errors and never end
                url_list = Bmark.query.outerjoin(Readable).\
                            filter(Readable.status_code != 200).all()

            else:
                url_list = Bmark.query.limit(PER_TRANS).offset(ct).all()

            if len(url_list) < PER_TRANS:
                all = True

            ct = ct + len(url_list)

            # build a list of urls to pass to the threads
            urls = dict([(bmark.hash_id, bmark.hashed.url) for bmark in url_list])
            parsed = {}

            # Set up some threads to fetch the enclosures
            for i in range(num_fetch_threads):
                # Download the feed(s) and put the enclosure URLs into
                # the queue.
                worker = threading.Thread(target=fetch_content, args=(i, enclosure_queue,))
                worker.setDaemon(True)
                worker.start()

            for hash_id, url in urls.iteritems():
                enclosure_queue.put((hash_id, url))

            # Now wait for the queue to be empty, indicating that we have
            # processed all of the downloads.
            enclosure_queue.join()

            # Set up some threads to fetch the enclosures
            for bmark in url_list:
                hashed = bmark.hashed

                read = parsed[bmark.hash_id]

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

            # let's do some count/transaction maint
            transaction.commit()
            transaction.begin()

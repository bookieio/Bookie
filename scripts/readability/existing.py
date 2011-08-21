"""Run readability on all of the existing urls in the databse


"""
import argparse
import logging
import transaction

from ConfigParser import ConfigParser
from os import path
from sqlalchemy import create_engine

from bookie.lib.readable import ReadUrl

from bookie.models import initialize_sql
from bookie.models import Hashed
from bookie.models import Readable

PER_TRANS = 10
LOG = logging.getLogger(__name__)


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

        db_url = ini.get('app:bookie', 'sqlalchemy.url')
        engine = create_engine(db_url, echo=False)
        initialize_sql(engine)

        ct = 0

        all = False
        while(not all):

            if args.new_only:
                # we take off the offset because each time we run, we should have
                # new ones to process. The query should return the 10 next
                # non-imported urls
                url_list = Hashed.query.outerjoin(Readable).\
                            filter(Readable.imported == None).\
                            limit(PER_TRANS).all()

            elif args.retry_errors:
                # we need a way to handle this query. If we offset and we clear
                # errors along the way, we'll skip potential retries
                # but if we don't we'll just keep getting errors and never end
                url_list = Hashed.query.outerjoin(Readable).\
                            filter(Readable.status_code != 200).all()

            else:
                url_list = Hashed.query.limit(PER_TRANS).offset(ct).all()

            if len(url_list) < PER_TRANS:
                all = True

            ct = ct + len(url_list)

            for hashed in url_list:
                print hashed.url

                read = ReadUrl.parse(hashed.url)
                if not read.is_image():
                    if not hashed.readable:
                        hashed.readable = Readable()

                    hashed.readable.content = read.content
                else:
                    if not hashed.readable:
                        hashed.readable = Readable()

                    hashed.readable.content = None

                # set some of the extra metadata
                hashed.readable.content_type = read.content_type
                hashed.readable.status_code = read.status
                hashed.readable.status_message = read.status_message

            # let's do some count/transaction maint
            transaction.commit()
            transaction.begin()

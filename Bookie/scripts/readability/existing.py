"""Run readability on all of the existing urls in the databse


"""
import argparse
import logging
import transaction
import urllib2

from ConfigParser import ConfigParser
from decruft import Document
from decruft import page_parser
from os import path
from sqlalchemy import create_engine

from bookie.lib.readable import ReadUrl

from bookie.models import initialize_sql
from bookie.models import DBSession
from bookie.models import Bmark
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

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

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

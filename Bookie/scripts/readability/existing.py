"""Run readability on all of the existing urls in the databse


"""
import argparse
import transaction
import urllib2

from ConfigParser import ConfigParser
from decruft import Document
from decruft import page_parser
from os import path
from sqlalchemy import create_engine

from bookie.models import initialize_sql

from bookie.models import DBSession
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Readable


def parse_args():
    """Parse out the command options. We want to support

    """
    desc = "Update existing bookbmarks with the readability parsed"

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--ini', dest='ini',
                            action='store',
                            default=None,
                            help='What .ini are we pulling the db connection from?')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    ini = ConfigParser()
    ini_path = path.join(path.dirname(path.dirname(path.dirname(__file__))), args.ini)
    ini.readfp(open(ini_path))

    db_url = ini.get('app:bookie', 'sqlalchemy.url')
    engine = create_engine(db_url, echo=False)
    initialize_sql(engine)

    url_list = Hashed.query.limit(5).all()

    for url in url_list:
        print url.url

        try:
            fh = urllib2.urlopen(url.url)
        except urllib2.HTTPError, exc:
            if url.readable:
                pass
            else:
                url.readable = Readable()

            url.readable.content = str(exc)

        # let's check to make sure we should be parsing this
        # for example: don't parse images
        headers = fh.info()
        ctype = headers.gettype()

        if 'image' not in ctype:
            if url.readable:
                pass
            else:
                url.readable = Readable()

            try:
                url.readable.content = Document(fh.read()).summary()
            except page_parser.Unparseable, exc:
                url.readable.content = str(exc)

    transaction.commit()

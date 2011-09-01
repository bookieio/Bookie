"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
import logging
import os
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh import qparser

from bookie.models import Bmark


LOG = logging.getLogger(__name__)
INDEX_NAME = 'bookie_index'


class BmarkSchema(SchemaClass):
    bid = ID(stored=True)
    description = TEXT
    extended = TEXT
    tags = KEYWORD
    readable = TEXT(analyzer=StemmingAnalyzer())

if not os.path.exists(INDEX_NAME):
    os.mkdir(INDEX_NAME)
    WIX = create_in(INDEX_NAME, BmarkSchema)
else:
    WIX = open_dir(INDEX_NAME)


def get_fulltext_handler(engine):
    """Based on the engine, figure out the type of fulltext interface"""
    return WhooshFulltext()


def get_writer():
    writer = WIX.writer()
    return writer


class WhooshFulltext(object):
    """Implement the fulltext api using whoosh as a storage backend

    """

    def search(self, phrase, content=False, username=None, ct=10, offset=0):
        """Implement the search, returning a list of bookmarks"""
        with WIX.searcher() as search:
            fields = ['description', 'extended', 'tags']
            if content:
                fields.append('readable')

            LOG.debug(fields)

            parser = qparser.MultifieldParser(fields,
                                           schema=WIX.schema,
                                           group=qparser.OrGroup)

            qry = parser.parse(phrase)
            LOG.debug(qry)

            res = search.search(qry, limit=None)
            LOG.debug(res)
            ids = [r['bid'] for r in res]
            LOG.debug('ids')
            LOG.debug(ids)
            qry = Bmark.query.filter(Bmark.bid.in_([r['bid'] for r in res]))
            qry = qry.options(joinedload('hashed'))

            return qry.all()

"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
import logging
import os

from sqlalchemy.orm import joinedload

from whoosh import qparser
from whoosh.fields import (
    BOOLEAN,
    ID,
    KEYWORD,
    SchemaClass,
    TEXT,
)
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.writing import AsyncWriter
from whoosh.query import (
    And,
    Or,
    Term,
)

from bookie.models import Bmark


LOG = logging.getLogger(__name__)
INDEX_NAME = None
INDEX_TYPE = None
WIX = None


def _reset_index():
    """Used by the test suite to reset the fulltext index."""
    WIX = create_in(INDEX_NAME, BmarkSchema)  # noqa


def set_index(index_type, index_path):
    global INDEX_NAME
    global INDEX_TYPE
    global WIX

    INDEX_TYPE = index_type
    INDEX_NAME = index_path

    cur_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    INDEX_NAME = os.path.join(cur_path, INDEX_NAME)

    if not os.path.exists(INDEX_NAME):
        os.mkdir(INDEX_NAME)
        WIX = create_in(INDEX_NAME, BmarkSchema)
    else:
        WIX = open_dir(INDEX_NAME)


class BmarkSchema(SchemaClass):
    bid = ID(unique=True, stored=True)
    description = TEXT
    extended = TEXT
    tags = KEYWORD
    readable = TEXT(analyzer=StemmingAnalyzer())
    username = ID
    is_private = BOOLEAN


def get_fulltext_handler(engine):
    """Based on the engine, figure out the type of fulltext interface"""
    global INDEX_TYPE
    if INDEX_TYPE == 'whoosh':
        return WhooshFulltext()


def get_writer():
    global WIX
    writer = AsyncWriter(WIX)
    return writer


class WhooshFulltext(object):
    """Implement the fulltext api using whoosh as a storage backend

    """
    global WIX

    def doc_count(self):
        with WIX.searcher() as search:
            return search.doc_count()

    def findByID(self, bid):
        """Find the item in the fulltext index by id"""
        with WIX.searcher() as search:
            found = search.documents(bid=unicode(bid))
            res = [b for b in found]
        if res:
            return res[0]
        else:
            return None

    def search(self, phrase, content=False, username=None, ct=10, page=0,
               requested_by=None):
        """Implement the search, returning a list of bookmarks"""
        page = int(page) + 1

        with WIX.searcher() as search:
            fields = ['description', 'extended', 'tags']

            if content:
                fields.append('readable')

            parser = qparser.MultifieldParser(fields,
                                              schema=WIX.schema,
                                              group=qparser.OrGroup)
            qry = parser.parse(phrase)

            if username:
                if requested_by and username == requested_by:
                    qry = And([
                        qry,
                        Or([
                            Term('is_private', 'f'),
                            And([
                                Term('username', username),
                                Term('is_private', 't')
                            ])
                        ])
                    ])
                else:
                    qry = And([qry, Term('username', username),
                              Term('is_private', 'f')])
            else:
                qry = And([qry, Term('is_private', 'f')])

            try:
                res = search.search_page(qry, page, pagelen=int(ct))
            except ValueError, exc:
                raise(exc)

            if res:
                qry = Bmark.query.filter(
                    Bmark.bid.in_([r['bid'] for r in res])
                )

                qry = qry.options(joinedload('hashed'))

                return qry.all()
            else:
                return []

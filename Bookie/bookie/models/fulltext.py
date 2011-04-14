"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
import logging
from sqlalchemy import text
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager

from bookie.models import SqliteBmarkFT
from bookie.models import SqliteContentFT
from bookie.models import Bmark
from bookie.models import Hashed
from bookie.models import Readable
from bookie.models import DBSession


LOG = logging.getLogger(__name__)


def get_fulltext_handler(engine):
    """Based on the engine, figure out the type of fulltext interface"""
    if 'sqlite' in engine:
        return SqliteFulltext()

    if 'mysql' in engine:
        return MySqlFulltext()

    if 'pg' in engine or 'postgres' in engine:
        return PgSqlFulltext()


class SqliteFulltext(object):
    """Extend the fulltext api object to implement searches for sqlite db

    The sqlite db uses the table fulltext to perform searches. We need to
    perform manuall db calls to that table for searches

    Columns: bid, description, extended, tags

    Storing is done automatically via the before_insert mapper hook on Bmark
    obj
    """
    def search(self, phrase, content=False):
        """Perform the search on the index"""
        #we need to adjust the phrase to be a set of OR per word
        phrase = " OR ".join(phrase.split())

        if not content:
            desc = SqliteBmarkFT.query.\
                        filter(SqliteBmarkFT.description.match(phrase))

            tag_str = SqliteBmarkFT.query.\
                        filter(SqliteBmarkFT.tag_string.match(phrase))

            ext = SqliteBmarkFT.query.\
                        filter(SqliteBmarkFT.extended.match(phrase))

            res = desc.union(tag_str, ext).join(SqliteBmarkFT.bmark).\
                        options(contains_eager(SqliteBmarkFT.bmark)).\
                        order_by('bmarks.stored').all()

            # everyone else sends a list of bmarks, so need to get our bmarks
            # out of the result set
            return [mark.bmark for mark in res]

        # check if we should be searching across the content table as well
        else:
            content = SqliteContentFT.query.\
                        filter(SqliteContentFT.content.match(phrase))

            hashed = aliased(Hashed)
            qry = content.outerjoin((hashed, SqliteContentFT.hashed)).\
                      options(contains_eager(SqliteContentFT.hashed,
                                             alias=hashed))

            bmarks = aliased(Bmark)
            qry = qry.outerjoin((bmarks, hashed.bmark)).\
                      options(contains_eager(SqliteContentFT.hashed,
                                             hashed.bmark,
                                             alias=bmarks))

            res = qry.order_by(bmarks.stored).all()
            results = []
            for read in res:
                LOG.debug(read)
                LOG.debug(read.hashed.bmark[0])
                results.append(read.hashed.bmark[0])

            return results


class MySqlFulltext(object):
    """Extend the fulltext api object to implement searches for mysql db

    Columns: bid, description, extended, tags

    """
    def search(self, phrase, content=False):
        """Perform the search on the index"""
        #we need to adjust the phrase to be a set of OR per word
        phrase = " OR ".join(phrase.split())

        if not content:
            desc = Bmark.query.\
                        filter(Bmark.description.match(phrase))

            tag_str = Bmark.query.\
                        filter(Bmark.tag_str.match(phrase))

            ext = Bmark.query.\
                        filter(Bmark.extended.match(phrase))

            return desc.union(tag_str, ext).\
                       order_by(Bmark.stored).all()
        else:
            content = Readable.query.\
                        filter(Readable.content.match(phrase))

            hashed = aliased(Hashed)
            qry = content.outerjoin((hashed, Readable.hashed)).\
                      options(contains_eager(Readable.hashed, alias=hashed))

            bmarks = aliased(Bmark)
            qry = qry.outerjoin((bmarks, hashed.bmark)).\
                      options(contains_eager(Readable.hashed,
                                             hashed.bmark,
                                             alias=bmarks))

            res = qry.order_by(bmarks.stored).all()
            results = []
            for read in res:
                LOG.debug(read)
                LOG.debug(read.hashed.bmark[0])
                results.append(read.hashed.bmark[0])

            return results


class PgSqlFulltext(object):
    """Implements a basic fulltext search of pgsql

    slow right now, to make faster need to setup a to_vector column for storing
    http://www.postgresql.org/docs/9.0/static/textsearch-tables.html

    """

    def search(self, phrase, content=False):
        """Need to perform searches against the three columns"""
        phrase = " | ".join(phrase.split())

        if not content:
            query = """SELECT bid
            FROM bmarks
            WHERE to_tsvector('english', description) @@ to_tsquery(:phrase) OR
                  to_tsvector('english', extended) @@ to_tsquery(:phrase) OR
                  to_tsvector('english', tag_str) @@ to_tsquery(:phrase)

            ORDER BY stored DESC;
            """

            res = DBSession.execute(text(query), {'phrase': phrase})

            ids = set([r.bid for r in res])

            return Bmark.query.join(Bmark.tags).\
                      options(contains_eager(Bmark.tags)).\
                      filter(Bmark.bid.in_(ids)).all()
        else:
            query = """SELECT readable.hash_id
            FROM readable, bmarks
            WHERE to_tsvector('english', content) @@ to_tsquery(:phrase)
                  AND readable.hash_id = bmarks.hash_id
            ORDER BY bmarks.stored DESC
            """

            res = DBSession.execute(text(query), {'phrase': phrase})

            ids = set([r.hash_id for r in res])

            return Bmark.query.join(Bmark.tags).\
                      options(contains_eager(Bmark.tags)).\
                      filter(Bmark.hash_id.in_(ids)).all()

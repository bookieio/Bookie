"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
import logging
from sqlalchemy import or_
from sqlalchemy import text
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

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
    def search(self, phrase, content=False, username=None):
        """Perform the search on the index"""
        #we need to adjust the phrase to be a set of OR per word
        phrase = " OR ".join(phrase.split())

        results = set()

        desc = SqliteBmarkFT.query.\
                    filter(SqliteBmarkFT.description.match(phrase))

        tag_str = SqliteBmarkFT.query.\
                    filter(SqliteBmarkFT.tag_string.match(phrase))

        ext = SqliteBmarkFT.query.\
                    filter(SqliteBmarkFT.extended.match(phrase))

        bmark = aliased(Bmark)
        qry = desc.union(tag_str, ext).join((bmark, SqliteBmarkFT.bmark)).\
                    options(contains_eager(SqliteBmarkFT.bmark, alias=bmark))

        if username:
            qry = qry.filter(bmark.username == username)

        res = qry.order_by(bmark.stored).all()

        # everyone else sends a list of bmarks, so need to get our bmarks
        # out of the result set
        results.update(set([mark.bmark for mark in res]))

        # check if we should be searching across the content table as well
        readable_res = []
        if content:
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

            if username:
                qry = qry.filter(bmark.username == username)

            res = qry.order_by(bmarks.stored).all()
            for read in res:
                readable_res.append(read.hashed.bmark[0])

        results.update(set(readable_res))
        return sorted(list(results), key=lambda res: res.stored, reverse=True)


def _mysql_postgres_search(phrase, content=False, username=None):
        """need to perform searches against the three columns"""
        phrase = " | ".join(phrase.split())

        filters = [
            Bmark.description.match(phrase),
            Bmark.extended.match(phrase),
            Bmark.tag_str.match(phrase)
        ]

        qry = Bmark.query.join(Bmark.tags).\
                  options(contains_eager(Bmark.tags)).\
                  options(joinedload('hashed'))

        if username:
            qry = qry.filter(Bmark.username == username)

        if content:
            LOG.debug('searching with content')
            readable = aliased(Readable)

            qry = qry.outerjoin((readable, Hashed.readable)).\
                  options(contains_eager(Bmark.hashed, Hashed.readable, alias=readable))

            filters.append(readable.content.match(phrase))

        bid_filter = DBSession.query(Bmark.bid.distinct()).\
                               filter(or_(*filters))
        qry = qry.filter(Bmark.bid.in_(bid_filter))


        qry = qry.join(Bmark.tags).\
                  options(contains_eager(Bmark.tags))

        results = qry.order_by(Bmark.stored.desc()).all()
        return results


class MySqlFulltext(object):
    """Extend the fulltext api object to implement searches for mysql db

    Columns: bid, description, extended, tags

    """
    def search(self, phrase, content=False, username=None):
        return _mysql_postgres_search(phrase,
                                      content=content,
                                      username=username)


class PgSqlFulltext(object):
    """Implements a basic fulltext search of pgsql

    slow right now, to make faster need to setup a to_vector column for storing
    http://www.postgresql.org/docs/9.0/static/textsearch-tables.html

    """

    def search(self, phrase, content=False, username=None):
        """need to perform searches against the three columns"""
        return _mysql_postgres_search(phrase,
                                      content=content,
                                      username=username)

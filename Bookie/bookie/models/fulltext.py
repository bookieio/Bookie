"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
from sqlalchemy import text
from sqlalchemy.orm import contains_eager

from bookie.models import SqliteModel
from bookie.models import Bmark
from bookie.models import DBSession


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

    Storing is done automatically via the before_insert mapper hook on Bmark obj
    """
    def search(self, phrase):
        """Perform the search on the index"""
        #we need to adjust the phrase to be a set of OR per word
        phrase = " OR ".join(phrase.split())

        desc = SqliteModel.query.\
                    filter(SqliteModel.description.match(phrase))

        tag_str = SqliteModel.query.\
                    filter(SqliteModel.tag_string.match(phrase))

        ext = SqliteModel.query.\
                    filter(SqliteModel.extended.match(phrase))

        res = desc.union(tag_str, ext).join(SqliteModel.bmark).\
                    options(contains_eager(SqliteModel.bmark)).\
                    order_by('bmarks.stored').all()

        # everyone else sends a list of bmarks, so need to get our bmarks out
        # of the result set
        return [mark.bmark for mark in res]


class MySqlFulltext(object):
    """Extend the fulltext api object to implement searches for mysql db

    Columns: bid, description, extended, tags

    """
    def search(self, phrase):
        """Perform the search on the index"""
        #we need to adjust the phrase to be a set of OR per word
        phrase = " OR ".join(phrase.split())

        desc = Bmark.query.\
                    filter(Bmark.description.match(phrase))

        tag_str = Bmark.query.\
                    filter(Bmark.tag_str.match(phrase))

        ext = Bmark.query.\
                    filter(Bmark.extended.match(phrase))

        return desc.union(tag_str, ext).\
                   order_by(Bmark.stored).all()



class PgSqlFulltext(object):
    """Implements a basic fulltext search of pgsql

    slow right now, to make faster need to setup a to_vector column for storing
    http://www.postgresql.org/docs/9.0/static/textsearch-tables.html

    """

    def search(self, phrase):
        """Need to perform searches against the three columns"""
        phrase = " | ".join(phrase.split())

        query = """SELECT bid
        FROM bmarks
        WHERE to_tsvector('english', description) @@ to_tsquery(:phrase) OR
              to_tsvector('english', extended) @@ to_tsquery(:phrase) OR
              to_tsvector('english', tag_str) @@ to_tsquery(:phrase)

        ORDER BY stored DESC;
        """

        res = DBSession.execute(text(query), {'phrase': phrase} )

        ids = set([r.bid for r in res])

        return Bmark.query.join(Bmark.tags).\
                  options(contains_eager(Bmark.tags)).\
                  filter(Bmark.bid.in_(ids)).all()

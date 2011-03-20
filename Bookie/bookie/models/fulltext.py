"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
from sqlalchemy.orm import contains_eager

from bookie.models import DBSession
from bookie.models import SqliteModel
from bookie.models import Bmark


def get_fulltext_handler(engine):
    """Based on the engine, figure out the type of fulltext interface"""
    if 'sqlite' in engine:
        return SqliteFulltext()


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

        res = SqliteModel.query.\
                    filter(SqliteModel.description.match(phrase)).\
                    join(SqliteModel.bmark).\
                    options(contains_eager(SqliteModel.bmark)).\
                    order_by('bmarks.stored')

        return res.all()

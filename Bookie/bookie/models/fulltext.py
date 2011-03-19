"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
from sqlalchemy.orm import contains_eager

from bookie.models import DBSession
from bookie.models import SqliteModel


class Fulltext(object):
    """Factory/API for the fulltext searches"""

    def __init__(self):
        """Init the object instance"""
        pass

    def __new__(self, cls, *args, **kwargs):
        """Determine the right type of fulltext to return"""
        # if DelImporter.can_handle(args[0]):
        return super(SqliteFulltext, cls).__new__(SqliteFulltext)

    def search(self, phrase):
        """Perform the search on the fulltext indexes"""
        raise NotImplementedError


class SqliteFulltext(Fulltext):
    """Extend the fulltext api object to implement searches for sqlite db

    The sqlite db uses the table fulltext to perform searches. We need to
    perform manuall db calls to that table for searches

    Columns: bid, description, extended, tags

    """

    @staticmethod
    def store(bmark):
        """Store the bmark instance into the fulltext db"""
        DBSession.add(SqliteModel(bmark.bid,
                                  bmark.description,
                                  bmark.extended,
                                  bmark.tag_string()))

    @staticmethod
    def search(phrase):
        """Perform the search on the index"""
        res = SqliteModel.query.\
                    filter(SqliteModel.description.match(phrase)).\
                    join(SqliteModel.bmark).\
                    options(contains_eager(SqliteModel.bmark))
        return res.all()

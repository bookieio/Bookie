"""Handle performaing fulltext searches against the database.

This is going to be dependant on the db model found so we'll setup a factory
and API as we did in the importer

"""
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import Table

from bookie.models import Base
from bookie.models import Base, DBSession

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
        res = SqliteModel.query.filter(SqliteModel.description.match(phrase))
        return res.all()


class SqliteModel(Base):
    """An SA model for the fulltext table used in sqlite"""
    __tablename__ = "fulltext"

    bid = Column(Integer, primary_key=True)
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    tags = Column(UnicodeText())

    def __init__(self, bid, description, extended, tag_string):
        """Expecting the properties to come from a Bmark instance

        tag_string is expected to be a concat list of strings from
        Bmark.tag_string()

        """
        self.bid = bid
        self.description = description
        self.extended = extended
        self.tags = tag_string

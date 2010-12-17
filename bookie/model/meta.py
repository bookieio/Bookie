"""SQLAlchemy Metadata and Session object"""
import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from pylons import config

__all__ = ['Session', 'metadata', 'Base']

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config


def todict(self):
    def convert_datetime(value):
        if value:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    d = {}
    for c in self.__table__.columns:
        if isinstance(c.type, sa.DateTime):
            value = convert_datetime(getattr(self, c.name))
        else:
            value = getattr(self, c.name)

        yield(c.name, value)


def iterfunc(self):
    """Returns an iterable that supports .next()
        so we can do dict(sa_instance)

    """
    return self.__todict__()

def fromdict(self, values):
    """Merge in items in the values dict into our object

       if it's one of our columns

    """
    for c in self.__table__.columns:
        if c.name in values:
            setattr(self, c.name, values[c.name])


# Setup the SQLAlchemy database engine
engine = None
Base = declarative_base()
metadata = Base.metadata
Session = scoped_session(sessionmaker())

Base.query = Session.query_property(Query)
Base.__todict__ = todict
Base.__iter__ = iterfunc
Base.fromdict = fromdict

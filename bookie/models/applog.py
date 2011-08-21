"""
Handle logging of the application stuff to the database

This will be replaced by something outside the app at some point, so the realy
code should all be in /lib/applogging.py vs in here. This is only the db store
side

"""
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText

from bookie.models import Base
from bookie.models import DBSession


class AppLogMgr(object):

    @staticmethod
    def store(**kwargs):
        """Store a new log record to the db"""
        stored = AppLog(**kwargs)
        DBSession.add(stored)


class AppLog(Base):
    __tablename__ = 'logging'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user = Column(Unicode(255), nullable=False)
    component = Column(Unicode(50), nullable=False)
    status = Column(Unicode(10), nullable=False)
    message = Column(Unicode(255), nullable=False)
    payload = Column(UnicodeText)
    tstamp = Column(DateTime, default=datetime.now)

    def __init__(self, **kwargs):
        self.user = kwargs.get('user', None)
        self.component = kwargs.get('component', None)
        self.status = kwargs.get('status', None)
        self.message = kwargs.get('message', None)
        self.payload = kwargs.get('payload', None)

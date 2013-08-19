"""
Handle logging of the application stuff to the database

This will be replaced by something outside the app at some point, so the realy
code should all be in /lib/applogging.py vs in here. This is only the db store
side

"""
from datetime import datetime
from datetime import timedelta

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import func
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

    @staticmethod
    def find(days=1, message_filter=None, status=None):
        """Find a set of app log records based on predefined filters."""
        qry = AppLog.query
        if status is not None:
            qry = qry.filter(AppLog.status == status)

        if message_filter:
            mfilter = '%{0}%'.format(message_filter)
            qry = qry.filter(func.lower(AppLog.message).like(mfilter))

        now = datetime.now()
        limit = now - timedelta(days=days)
        qry = qry.filter(AppLog.tstamp > limit)

        return qry.order_by(AppLog.tstamp.desc()).all()


class AppLog(Base):
    __tablename__ = 'logging'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user = Column(Unicode(255), nullable=False)
    component = Column(Unicode(50), nullable=False)
    status = Column(Unicode(10), nullable=False)
    message = Column(Unicode(255), nullable=False)
    payload = Column(UnicodeText)
    tstamp = Column(DateTime, default=datetime.now)

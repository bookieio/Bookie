from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode

from bookie.models import Base

NEW = 0
RUNNING = 1
COMPLETE = 2
ERROR = 3


class ImportQueueMgr(object):
    """All the static methods for ImportQueue"""

    @staticmethod
    def get(id):
        """Get the import item"""
        return ImportQueue.query.get(id)

    @staticmethod
    def size():
        """How deep is the queue at the moment"""
        qry = ImportQueue.query.filter(ImportQueue.completed != None)
        return qry.count()



    @staticmethod
    def get_ready(limit=10):
        """Get a list of imports that need to be processed"""
        qry = ImportQueue.query.filter(ImportQueue.status == 0)
        return qry.limit(limit).all()


class ImportQueue(Base):
    """Track imports we need to do"""
    __tablename__ = 'import_queue'

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Unicode(255))
    file_path = Column(Unicode(100), nullable=False)
    tstamp = Column(DateTime, default=datetime.now)
    status = Column(Integer, default=NEW)
    completed = Column(DateTime)

    def __init__(self, username, file_path):
        """Start up an import queue"""
        self.username = username
        self.file_path = file_path

    def mark_error(self):
        """Mark that this failed and was an error"""
        self.status = ERROR

    def mark_running(self):
        """Mark that we're processing this"""
        self.status = RUNNING

    def mark_done(self):
        """Mark it complete"""
        self.completed = datetime.now()
        self.status = COMPLETE

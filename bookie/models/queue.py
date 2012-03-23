import logging
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import or_
from sqlalchemy import Unicode

from bookie.models import Base

LOG = logging.getLogger(__name__)

NEW = 0
RUNNING = 1
COMPLETE = 2
ERROR = 3


class ImportQueueMgr(object):
    """All the static methods for ImportQueue"""

    @staticmethod
    def get(id=None, username=None, status=None):
        """Get the import item"""
        if (id):
            qry = ImportQueue.query.filter(ImportQueue.id==id)
        elif (username):
            qry = ImportQueue.query.filter(ImportQueue.username==username)

        if status is not None:
            qry = qry.filter(ImportQueue.status==status)

        return qry.first()

    @staticmethod
    def get_details(id=None, username=None):
        """Get some details about a import

        We want to offer things like where they are in queue and maybe the
        import record itself

        """
        your_import = ImportQueueMgr.get(id=id, username=username)
        place_qry = ImportQueue.query.filter(ImportQueue.status==NEW)
        place_qry = place_qry.filter(ImportQueue.id < your_import.id)

        return {
            'place': place_qry.count(),
            'import': your_import
        }

    @staticmethod
    def get_ready(limit=10):
        """Get a list of imports that need to be processed"""
        qry = ImportQueue.query.filter(ImportQueue.status == 0)
        return qry.limit(limit).all()

    @staticmethod
    def size():
        """How deep is the queue at the moment"""
        qry = ImportQueue.query.filter(or_(
            ImportQueue.status != COMPLETE,
            ImportQueue.status != ERROR))
        return qry.count()

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

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime

from bookie.models import Base

class Readable(Base):
    """Handle the storing of the readable version of the page content"""
    __tablename__ = 'readable'

    hash_id = Column(Unicode(22),
                     ForeignKey('url_hash.hash_id'),
                     primary_key=True)
    content = Column(UnicodeText)
    imported = Column(DateTime, default=datetime.now)

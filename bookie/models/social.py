
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Unicode,
    Boolean)

from bookie.models import Base


class BaseConnection(Base):
    """Table to store User basic social information"""
    __tablename__ = "BaseConnection"
    id = Column(Integer, primary_key=True)
    username = Column(Unicode(255),
                      ForeignKey('users.username'))
    type = Column(Unicode(255))
    is_active = Column(Boolean, default=False)
    last_connection = Column(DateTime, onupdate=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'BaseConnection',
        'polymorphic_on': type
    }


class TwitterConnection(BaseConnection):
    """ Table to store User Twitter information"""
    __tablename__ = "TwitterConnection"

    connection_id = Column(Integer, ForeignKey('BaseConnection.id'),
                           primary_key=True)

    # User Twitter Data
    uid = Column(Unicode(255))
    access_key = Column(Unicode(255))
    access_secret = Column(Unicode(255))
    twitter_username = Column(Unicode(255))
    refresh_date = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'TwitterConnection'
    }

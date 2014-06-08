
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Unicode,
    Boolean)

from bookie.models import Base

twitter_connection = 'TwitterConnection'


class SocialMgr(object):
    """Class to handle non-instance BaseConnection functions"""
    @staticmethod
    def get_all_connections(username):
        connections = BaseConnection.query.filter(
            BaseConnection.username == username)
        return connections


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
    __tablename__ = twitter_connection

    connection_id = Column(Integer, ForeignKey('BaseConnection.id'),
                           primary_key=True)

    # User Twitter Data
    uid = Column(Unicode(255))
    access_key = Column(Unicode(255))
    access_secret = Column(Unicode(255))
    twitter_username = Column(Unicode(255))
    refresh_date = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity': twitter_connection
    }

    def __todict__(self):
        yield('username', self.username)
        yield('type', self.type)
        social_info = {}
        social_info['uid'] = self.uid
        social_info['twitter_username'] = self.twitter_username
        social_info['refresh_date'] = str(self.refresh_date)
        yield('twitter_connection', social_info)
        yield('last_connection', str(self.last_connection))

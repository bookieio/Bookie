
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Unicode,
    Boolean)

from bookie.models import Base
from bookie.models import DBSession

twitter_connection = 'TwitterConnection'


class SocialMgr(object):
    """Class to handle non-instance BaseConnection functions"""
    @staticmethod
    def get_all_connections(username):
        connections = BaseConnection.query.filter(
            BaseConnection.username == username)
        return connections

    @staticmethod
    def get_twitter_connections(username=None):
        """ Returns all twitter connections based on username """
        if username:
            connections = TwitterConnection.query.filter(
                TwitterConnection.username == username).all()
        else:
            connections = TwitterConnection.query.all()
        return connections

    @staticmethod
    def store_twitter_connection(username, credentials):
        tconnection = TwitterConnection(
            username=username,
            is_active=credentials['is_active'],
            last_connection=credentials['last_connection'],
            uid=credentials['uid'],
            access_key=credentials['access_key'],
            access_secret=credentials['access_secret'],
            twitter_username=credentials['twitter_username'],
            refresh_date=credentials['refresh_date'])
        DBSession.add(tconnection)
        return tconnection

    @staticmethod
    def update_last_tweet_data(connection, tweet_id):
        connection.last_tweet_seen = tweet_id
        connection.refresh_date = datetime.now()
        return connection


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
    last_tweet_seen = Column(Unicode(255))

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

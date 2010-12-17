from bookie_app.model import meta
from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, Boolean

class UserManager(object):
    """Tools for managing anon/groups of bookmarks

    """
    pass

class User(meta.Base):
    """SA Model for users table"""
    __tablename__ = 'users'

    id = Column(Integer(), primary_key=True)
    username = Column(Unicode(255))
    email = Column(Unicode(255))
    salt = Column(Unicode(10))


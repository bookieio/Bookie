from bookie_app import model
from bookie_app.model import meta

from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, Boolean
from sqlalchemy.sql.expression import desc, asc
from sqlalchemy.orm import relationship, joinedload

from hashlib import sha1
from datetime import datetime

from bookie_app.model.tied_tables import bookmark_tags_table
from bookie_app.model.tags import Tag

class BookmarkManager(object):
    """Tools for managing anon/groups of bookmarks"""
    
    @staticmethod
    def get_list(with_tags=False, **kwargs):
        """Fetch a list of Bookmarks

        :param with_tags: Preload the tied tags to the bookmarks on query
        :param limit: integer limit for the result set
        :param order_by: column name to sort on
        :param order: constant from model module to specify sort order

        """
        if with_tags:
            query = Bookmark.query.options(joinedload(Bookmark.tags))
        else:
            query = Bookmark.query

        query = model.QueryCleaner(query, **kwargs)
        return query.query.all()

class Bookmark(meta.Base):
    """SA Model for bookmarks table"""
    __tablename__ = 'bookmarks'

    id = Column(Integer(), primary_key=True)
    hash = Column(Unicode(40), unique=True)
    url = Column(UnicodeText())
    added = Column(DateTime, default=datetime.now)
    updated = Column(DateTime)

    tags = relationship("Tag", backref="bookmarks", secondary=bookmark_tags_table)

    def __init__(self, url):
        """Create a new bookmark

        :param url: string of the url to bookmark, gets hashed into the id

        """
        id_hash = sha1()
        id_hash.update(url)
        self.hash = id_hash.hexdigest()
        self.url = url

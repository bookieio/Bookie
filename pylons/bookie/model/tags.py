from bookie_app import model
from bookie_app.model import meta
from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, Boolean

class TagManager(object):
    """Tools for managing anon/groups of tags

    :param limit: integer limit for the result set
    :param order_by: column name to sort on
    :param order: constant from model module to specify sort order

    """
    @staticmethod
    def get_list(tag_names=None, **kwargs):
        """Fetch a list of tags

        :param limit: integer limit for the result set
        :param order_by: column name to sort on
        :param order: constant from model module to specify sort order

        """
        query = model.QueryCleaner(Tag.query, **kwargs)

        if tag_names:
            query.query = query.query.filter(Tag.name.in_(tag_names))

        return query.query.all()

    @staticmethod
    def parse(tag_string, store=False):
        """Parse a string of tags into a list of tag objects

        :param tag_string: the string from a api submit/etc
        :param store: If True, save any tags that do not exist

        """
        tag_list = tag_string.split(" ")

        found_list = TagManager.get_list(tag_names = tag_list)
        found_names = [tag.name for tag in found_list]

        for tag in tag_list:
            if tag not in found_names:
                t = Tag(tag)
                meta.Session.add(t)
                found_list.append(t)

        return found_list

class Tag(meta.Base):
    """SA Model for tags table
    
    
    :Note: bookmarks parameter available via bookmark backref 
    """
    __tablename__ = 'tags'

    id = Column(Integer(), primary_key=True)
    name = Column(Unicode(50))
    count = Column(Integer(), default=0)

    def __init__(self, tag_name):
        self.name = tag_name
        self.count = 0


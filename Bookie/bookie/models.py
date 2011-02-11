from datetime import datetime
import transaction

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import Table

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relation
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.collections import attribute_mapped_collection

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def todict(self):
    """Method to turn an SA instance into a dict so we can output to json"""

    def convert_datetime(value):
        """We need to treat datetime's special to get them to json"""
        if value:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    for col in self.__table__.columns:
        if isinstance(col.type, sa.DateTime):
            value = convert_datetime(getattr(self, col.name))
        else:
            value = getattr(self, col.name)

        yield(col.name, value)


def iterfunc(self):
    """Returns an iterable that supports .next()
        so we can do dict(sa_instance)

    """
    return self.__todict__()


def fromdict(self, values):
    """Merge in items in the values dict into our object

       if it's one of our columns

    """
    for col in self.__table__.columns:
        if col.name in values:
            setattr(self, col.name, values[col.name])


# Setup the SQLAlchemy database engine
Base.query = DBSession.query_property(Query)
Base.__todict__ = todict
Base.__iter__ = iterfunc
Base.fromdict = fromdict

bmarks_tags = Table('bmark_tags', Base.metadata,
    Column('bmark_id', Integer, ForeignKey('bmarks.bid'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tid'), primary_key=True)
)


class TagMgr(object):
    """Handle all non-instance related tags functions"""

    @staticmethod
    def from_string(tag_str):
        """Split a list of tags in string form to instances

        Currently it only supports space delimited

        """
        tag_list = tag_str.split(" ")
        tag_objects = {}

        for tag in TagMgr.find(tags=tag_list):
            # remove the tag from the tag_list as we find it
            tag_objects[tag.name] = tag
            tag_list.remove(tag.name)

        # any tags left in the list are new
        for new_tag in tag_list:
            tag_objects[new_tag] = Tag(new_tag)

        return tag_objects

    @staticmethod
    def find(tags=None):
        """Find all of the tags in the system"""
        qry = Tag.query

        if tags:
            # limit to only the tag names in this list
            qry.filter(Tag.name.in_(tags))

        return qry.all()


class Tag(Base):
    """Bookmarks can have many many tags"""
    __tablename__ = "tags"

    tid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True)

    def __init__(self, tag_name):
        self.name = tag_name


class BmarkMgr(object):
    """Class to handle non-instance Bmark functions"""

    @staticmethod
    def get_by_url(url):
        """Get a bmark from the system via the url"""
        return Bmark.query.find(url).one()


class Bmark(Base):
    """Basic bookmark table object"""
    __tablename__ = "bmarks"

    bid = Column(Integer, autoincrement=True, primary_key=True)
    url = Column(UnicodeText(), unique=True)
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    stored = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)

    tags = relation(Tag,
            backref="bmark",
            collection_class=attribute_mapped_collection('name'),
            secondary=bmarks_tags,
    )

    def __init__(self, url, desc=None, ext=None, tags=None):
        """Create a new bmark instance

        :param url: string of the url to be added as a bookmark

        :param desc: Description field, optional
        :param ext: Extended desc field, optional
        :param tags: Space sep list of Bookmark tags, optional

        """
        self.url = url
        self.description = desc
        self.extended = ext

        # tags are space separated
        self.tags = TagMgr.from_string(tags)

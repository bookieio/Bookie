"""Sqlalchemy Models for objects stored with Bookie"""
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import Table

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import contains_eager
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
    """Called by the app on startup to setup bindings to the DB"""
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine


def todict(self):
    """Method to turn an SA instance into a dict so we can output to json"""

    def convert_datetime(value):
        """We need to treat datetime's special to get them to json"""
        if value:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""

    for col in self.__table__.columns:
        if isinstance(col.type, DateTime):
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
        if tag_str == '':
            return {}

        tag_list = set(tag_str.split(" "))
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
    def find(order_by=None, tags=None):
        """Find all of the tags in the system"""
        qry = Tag.query

        if tags:
            # limit to only the tag names in this list
            qry = qry.filter(Tag.name.in_(tags))

        if order_by is not None:
            qry = qry.order_by(order_by)
        else:
            qry = qry.order_by(Tag.name)

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
        # normalize the url
        clean_url = BmarkTools.normalize_url(url)
        return Bmark.query.filter(Bmark.url == clean_url).one()

    @staticmethod
    def find(order_by=None, limit=50, page=0, with_tags=False):
        """Search for specific sets of bookmarks"""
        qry = Bmark.query

        if order_by is not None:
            qry = qry.order_by(order_by)
        else:
            qry = qry.order_by(Bmark.bid.desc())

        offset = limit * page
        qry = qry.limit(limit).offset(offset).from_self()

        if with_tags:
            qry = qry.join(Bmark.tags).\
                      options(contains_eager(Bmark.tags))

        return qry.all()

    @staticmethod
    def by_tag(tag, limit=50, page=0):
        """Get a recent set of bookmarks"""
        qry = Bmark.query.join(Bmark.tags).\
                  options(contains_eager(Bmark.tags)).\
                  filter(Tag.name == tag)

        offset = limit * page
        qry = qry.order_by(Bmark.stored.desc()).\
                  limit(limit).\
                  offset(offset).\
                  from_self()

        qry = qry.outerjoin(Bmark.tags).\
                  options(contains_eager(Bmark.tags))

        return qry.all()

    @staticmethod
    def recent(limit=50, page=0, with_tags=False):
        """Get a recent set of bookmarks"""
        qry = Bmark.query

        offset = limit * page
        qry = qry.order_by(Bmark.stored.desc()).\
                  limit(limit).\
                  offset(offset).\
                  from_self()

        if with_tags:
            qry = qry.outerjoin(Bmark.tags).\
                      options(contains_eager(Bmark.tags))

        return qry.all()


class BmarkTools(object):
    """Some stupid tools to help work with bookmarks"""

    @staticmethod
    def normalize_url(url):
        """We need to clean the url so that we can easily find/check for dupes

        Things to do:
        - strip any trailing spaces
        - Leave any query params, but think about removing common ones like
          google analytics stuff utm_*

        """
        url = url.strip().strip('/')
        return url


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
        self.url = BmarkTools.normalize_url(url)
        self.description = desc
        self.extended = ext

        # tags are space separated
        self.tags = TagMgr.from_string(tags)

    def __str__(self):
        return "<Bmark: {0}:{1}>".format(self.bid, self.url)

    def tag_string(self):
        """Generate a single spaced string of our tags"""
        return " ".join([tag for tag in self.tags.iterkeys()])

    def update_tags(self, tag_string):
        """Given a tag string, split and update our tags to be these"""
        self.tags = TagMgr.from_string(tag_string)


class SqliteModel(Base):
    """An SA model for the fulltext table used in sqlite"""
    __tablename__ = "fulltext"

    bid = Column(Integer,
                    ForeignKey('bmarks.bid'),
                    primary_key=True,)
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    tags = Column(UnicodeText())
    bmark = relation(Bmark,
                     backref='fulltext',
                     uselist=False,)

    def __init__(self, bid, description, extended, tag_string):
        """Expecting the properties to come from a Bmark instance

        tag_string is expected to be a concat list of strings from
        Bmark.tag_string()

        """
        self.bid = bid
        self.description = description
        self.extended = extended
        self.tag_string = tag_string

"""Sqlalchemy Models for objects stored with Bookie"""
import logging
import shortuuid

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

from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import relation
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.orm.collections import attribute_mapped_collection

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

LOG = logging.getLogger(__name__)


def initialize_sql(engine):
    """Called by the app on startup to setup bindings to the DB"""
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # only if we are on sqlite do we have this relation
    if 'sqlite' in str(DBSession.bind):

        if not hasattr(SqliteModel, 'bmark'):
            Bmark.fulltext = relation(SqliteModel,
                         backref='bmark',
                         uselist=False,
                         cascade="all, delete, delete-orphan",
                         )


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

        tag_list = set([tag.lower().strip() for tag in tag_str.split(" ")])
        tag_objects = {}

        for tag in TagMgr.find(tags=tag_list):
            tag_objects[tag.name.lower()] = tag
            tag_list.remove(tag.name.lower())

        # any tags left in the list are new
        for new_tag in (tag for tag in tag_list if tag != ""):
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


class SqliteModel(Base):
    """An SA model for the fulltext table used in sqlite"""
    __tablename__ = "fulltext"

    bid = Column(Integer,
                    ForeignKey('bmarks.bid'),
                    primary_key=True,)
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    tag_string = Column(UnicodeText())

    def __init__(self, bid, description, extended, tag_string):
        """Expecting the properties to come from a Bmark instance

        tag_string is expected to be a concat list of strings from
        Bmark.tag_string()

        """
        self.bid = bid
        self.description = description
        self.extended = extended
        self.tag_string = tag_string


class FullTextExtension(MapperExtension):
    """This is a mapper to handle inserting into fulltext index

    Since the sqlite fulltext is a separate table, we need to insert/update
    into that fulltext index whenever we add/change a bookmark

    Other dbs need to have the concat tag_str populated to search against

    """
    def before_insert(self, mapper, connection, instance):
        # we need to update the fulltext instance for this bmark instance
        # we only do this for sqlite connections, else just pass
        if 'sqlite' in str(DBSession.bind):
            LOG.error('called before insert')
            LOG.error(instance.__repr__())
            instance.fulltext = SqliteModel(instance.bid,
                                  instance.description,
                                  instance.extended,
                                  instance.tag_string())
        else:
            instance.tag_str = instance.tag_string()


class HashedMgr(object):
    """Manage non-instance methods of Hashed objects"""
    @staticmethod
    def get_by_url(url):
        """Return a hashed object for the url specified"""
        res = Hashed.query.filter(Hashed.url==url).all()
        if res:
            return res[0]
        else:
            return False


class Hashed(Base):
    """The hashed url string and some metadata"""
    __tablename__ = "url_hash"

    hash_id = Column(Unicode(22), primary_key=True)
    url = Column(UnicodeText, unique=True)
    clicks= Column(Integer, default=0)

    def __init__(self, url):
        """We'll auto hash the id for them and set this up"""
        self.hash_id = shortuuid.uuid(url=str(url))
        self.url = url


class BmarkMgr(object):
    """Class to handle non-instance Bmark functions"""

    @staticmethod
    def get_by_url(url):
        """Get a bmark from the system via the url"""
        # normalize the url
        clean_url = BmarkTools.normalize_url(url)
        return Bmark.query.join(Bmark.hashed).\
                           options(contains_eager(Bmark.hashed)).\
                           filter(Hashed.url == clean_url).one()

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
        """Get a set of bookmarks with the given tag"""
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

    @staticmethod
    def popular(limit=50, page=0, with_tags=False):
        """Get the bookmarks by most popular first"""
        qry = Hashed.query

        offset = limit * page
        qry = qry.order_by(Hashed.clicks.desc()).\
                  limit(limit).\
                  offset(offset).\
                  from_self()

        bmark = aliased(Bmark)
        qry = qry.join((bmark, Hashed.bmark)).\
                  options(contains_eager(Hashed.bmark, alias=bmark))

        tags = aliased(Tag)
        if with_tags:
            qry = qry.outerjoin((tags, bmark.tags)).\
                      options(contains_eager(Hashed.bmark, bmark.tags, alias=tags))
        res = qry.all()
        return res


    @staticmethod
    def store(url, desc, ext, tags, dt=None, fulltext=None):
        """Store a bookmark

        :param url: bookmarked url
        :param desc: the one line description
        :param ext: the extended description/notes
        :param dt: The original stored time of this bmark
        :param fulltext: an instance of a fulltext handler

        """
        mark = Bmark(url,
                     desc=desc,
                     ext=ext,
                     tags=tags,
               )

        DBSession.add(mark)

        # if we have a dt then manually set the stored value
        if dt is not None:
            mark.stored = dt

        # now index it into the fulltext db as well
        if fulltext:
            DBSession.flush()


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
    __mapper_args__ = {
        'extension': FullTextExtension()
    }

    bid = Column(Integer, autoincrement=True, primary_key=True)
    hash_id = Column(Unicode(22), ForeignKey('url_hash.hash_id'), unique=True)
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    stored = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)

    # DON"T USE
    tag_str = Column(UnicodeText())

    tags = relation(Tag,
            backref="bmark",
            collection_class=attribute_mapped_collection('name'),
            secondary=bmarks_tags,
            lazy='joined',
            innerjoin=False,
    )

    hashed = relation(Hashed,
                      backref="bmark",
                      uselist=False,)


    def __init__(self, url, desc=None, ext=None, tags=None):
        """Create a new bmark instance

        :param url: string of the url to be added as a bookmark

        :param desc: Description field, optional
        :param ext: Extended desc field, optional
        :param tags: Space sep list of Bookmark tags, optional

        """
        # if we already have this url hashed, get that hash
        existing = HashedMgr.get_by_url(url)

        if not existing:
            self.hashed = Hashed(url)
        else:
            self.hashed = existing

        self.description = desc
        self.extended = ext

        # tags are space separated
        self.tags = TagMgr.from_string(tags)

    def __str__(self):
        return "<Bmark: {0}:{1}>".format(self.bid, self.hashed.url)

    def tag_string(self):
        """Generate a single spaced string of our tags"""
        return " ".join([tag for tag in self.tags.iterkeys()])

    def update_tags(self, tag_string):
        """Given a tag string, split and update our tags to be these"""
        self.tags = TagMgr.from_string(tag_string)




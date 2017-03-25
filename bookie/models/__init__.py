"""Sqlalchemy Models for objects stored with Bookie"""
import logging

from topia.termextract import extract
from BeautifulSoup import BeautifulSoup
from bookie.lib.urlhash import generate_hash

from datetime import datetime

from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import select
from unidecode import unidecode
from urlparse import urlparse

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import relation
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError   # noqa
from sqlalchemy.orm.exc import NoResultFound  # noqa

from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import func
from sqlalchemy.sql import and_

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

LOG = logging.getLogger(__name__)


def initialize_sql(settings):
    """Called by the app on startup to setup bindings to the DB"""
    engine = engine_from_config(settings, 'sqlalchemy.')

    if not DBSession.registry.has():
        DBSession.configure(bind=engine)
        Base.metadata.bind = engine

    import bookie.models.fulltext as ft
    ft.set_index(settings.get('fulltext.engine'),
                 settings.get('fulltext.index'))

    # setup the User relation, we've got import race conditions, ugh
    from bookie.models.auth import User
    if not hasattr(Bmark, 'user'):
        Bmark.user = relation(User,
                              backref="bmark")


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

bmarks_tags = Table(
    'bmark_tags', Base.metadata,
    Column('bmark_id', Integer, ForeignKey('bmarks.bid'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.tid'), primary_key=True)
)


class InvalidBookmark(Exception):
    """Exception class for erroring when a bookmark is not a valid one."""


class TagMgr(object):
    """Handle all non-instance related tags functions"""

    @staticmethod
    def from_string(tag_str):
        """Split a list of tags in string form to instances

        Currently it only supports space delimited

        """
        if not tag_str or tag_str == u'':
            return {}

        tag_list = set([tag.lower().strip() for tag in tag_str.split(u" ")])
        tag_objects = {}

        for tag in TagMgr.find(tags=tag_list):
            tag_objects[tag.name.lower()] = tag
            tag_list.remove(tag.name.lower())

        # any tags left in the list are new
        for new_tag in (tag for tag in tag_list if tag != ""):
            tag_objects[new_tag] = Tag(new_tag)

        return tag_objects

    @staticmethod
    def find(order_by=None, tags=None, username=None):
        """Find all of the tags in the system"""
        qry = Tag.query

        if tags:
            # limit to only the tag names in this list
            qry = qry.filter(Tag.name.in_(tags))

        if username:
            # then we'll need to bind to bmarks to be able to limit on the
            # username field
            bmark = aliased(Bmark)
            qry = qry.join((bmark, Tag.bmark)).\
                filter(bmark.username == username)

        if order_by is not None:
            qry = qry.order_by(order_by)
        else:
            qry = qry.order_by(Tag.name)

        return qry.all()

    @staticmethod
    def complete(prefix, current=None, limit=5, username=None,
                 requested_by=None):
        """Find all of the tags that begin with prefix

        :param current: a list of current tags to compare with

        If we provide a current then we should only complete tags that have
        bookmarks with the current tag AND starts with the new prefix. In this
        way when filtering tags we only complete things that make sense to
        complete

        """
        prefix = prefix.lower()
        if current is None:
            qry = Tag.query.filter(Tag.name.startswith(prefix))

            # if we have a username limit to only bookmarks of that user
            if username:
                qry = qry.filter(Tag.bmark.any(username=username))
                # If username == requested_by, we want all the bookmarks so,
                # no need to filter on is_private.
                # If username != requested_by, we want to limit to only
                # public bookmarks.
                if username != requested_by:
                    bmark = aliased(Bmark)
                    qry = qry.join((bmark, Tag.bmark)).\
                        filter(bmark.is_private == False)   # noqa
            else:
                bmark = aliased(Bmark)
                qry = qry.join((bmark, Tag.bmark)).\
                    filter(bmark.is_private == False)   # noqa

            qry = qry.order_by(Tag.name).limit(limit)
            return qry.all()

        else:
            # things get a bit more complicated
            """
                SELECT DISTINCT(tag_id), tags.name
                FROM bmark_tags
                JOIN tags ON bmark_tags.tag_id = tags.tid
                WHERE bmark_id IN (
                    SELECT bmark_id FROM bmark_tags WHERE tag_id IN (
                        SELECT DISTINCT(t.tid) FROM tags t
                            WHERE t.name in ('vagrant', 'tips')
                    )
                )
                AND tags.name LIKE ('ub%');
            """
            current_tags = DBSession.query(Tag.tid).\
                filter(Tag.name.in_(current)).group_by(Tag.tid)

            good_bmarks = DBSession.query(Bmark.bid)

            if username:
                good_bmarks = good_bmarks.filter(Bmark.username == username)
                if username != requested_by:
                    good_bmarks = good_bmarks.\
                        filter(Bmark.is_private == False)   # noqa
            else:
                good_bmarks = good_bmarks.\
                    filter(Bmark.is_private == False)   # noqa

            good_bmarks = good_bmarks.\
                filter(Bmark.tags.any(Tag.tid.in_(current_tags))).\
                group_by(Bmark.bid)

            query = DBSession.query(Tag.name.distinct().label('name')).\
                filter(Tag.name.startswith(prefix)).\
                filter(Tag.bmark.any(Bmark.bid.in_(good_bmarks)))

            return DBSession.execute(query)

    @staticmethod
    def suggestions(bmark=None, url=None, username=None):
        """Find suggestions for tags for an existing bookmark

        The plan:
            Suggest tags based on the readable content of the Bookmark
            that the user is editing. New Bookmarks won't end up here.

        """
        tag_suggest = []
        tag_list = []

        #  If url is None return empty tags
        if url is None:
            return tag_list
        else:
            bmark = BmarkMgr.get_by_url(url)
            # If bmark is not parsed return empty tag list
            if bmark.readable is None:
                return tag_list
            # Some times parsing may fail and we cannot parse the webpage
            # then satus_code will be set to 900
            elif bmark.readable.status_code == '900':
                return tag_list
            else:
                content = bmark.readable.content
                # Remove unicode character while printing
                clean_content = (
                    "".join(
                        BeautifulSoup(content).findAll(text=True)).encode(
                        'ascii', 'ignore'))
                get_tags = extract.TermExtractor()
                tag_suggest = get_tags(clean_content)
                tag_suggest = sorted(tag_suggest, key=lambda tag_suggest:
                                     tag_suggest[1], reverse=True)
                for result in tag_suggest:
                    # If it has a space in it, split it.
                    tags = result[0].split()
                    for tag in tags:
                        # Require at least 3 chars long and ignore pure
                        # numbers.
                        if tag not in tag_list and tag not in bmark.tags:
                            if len(tag) > 2 and not tag.isdigit():
                                tag_list.append(tag.lower())
                return tag_list

    @staticmethod
    def count():
        """Count how many tags we have in the system"""
        return Tag.query.count()


class Tag(Base):
    """Bookmarks can have many many tags"""
    __tablename__ = "tags"

    tid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True)

    def __init__(self, tag_name):
        self.name = tag_name.lower()


class ReadableMgr(object):
    """Handle non-instance model issues for readable"""
    pass


class Readable(Base):
    """Handle the storing of the readable version of the page content"""
    __tablename__ = 'bmark_readable'

    bid = Column(Integer,
                 ForeignKey('bmarks.bid'),
                 primary_key=True)
    hash_id = Column(Unicode(22),
                     ForeignKey('bmarks.hash_id'),
                     index=True)
    content = Column(UnicodeText)
    clean_content = Column(UnicodeText)
    imported = Column(DateTime, default=datetime.utcnow)
    content_type = Column(Unicode(255))
    status_code = Column(Integer)
    status_message = Column(Unicode(255))


def sync_readable_content(mapper, connection, target):
    def _clean_content(content):
        if content:
            return u' '.join(BeautifulSoup(content).findAll(text=True))
        else:
            return u""

    target.clean_content = _clean_content(target.content)

    # Background the process of fulltext indexing this bookmark's content.
    from bookie.bcelery import tasks
    tasks.fulltext_index_bookmark.delay(
        target.bmark.bid,
        target.clean_content)


event.listen(Readable, 'after_insert', sync_readable_content)
event.listen(Readable, 'after_update', sync_readable_content)


class HashedMgr(object):
    """Manage non-instance methods of Hashed objects"""

    def count(self):
        """Count how many unique hashed urls we've got."""
        return Hashed.query.count()

    @staticmethod
    def get_by_url(url):
        """Return a hashed object for the url specified"""
        res = Hashed.query.filter(Hashed.url == url).all()
        if res:
            return res[0]
        else:
            return False


class Hashed(Base):
    """The hashed url string and some metadata"""
    __tablename__ = "url_hash"

    hash_id = Column(Unicode(22), primary_key=True)
    url = Column(UnicodeText)
    clicks = Column(Integer, default=0)

    def __init__(self, url):
        """We'll auto hash the id for them and set this up"""
        cleaned_url = str(unidecode(url))
        self.hash_id = unicode(generate_hash(cleaned_url))
        self.url = url


class BmarkMgr(object):
    """Class to handle non-instance Bmark functions"""

    @staticmethod
    def get_by_url(url, username=None):
        """Get a bmark from the system via the url"""
        # normalize the url
        clean_url = BmarkTools.normalize_url(url)

        qry = Bmark.query.join(Bmark.hashed).\
            options(contains_eager(Bmark.hashed)).\
            filter(Hashed.url == clean_url)

        if username:
            qry = qry.filter(Bmark.username == username)

        return qry.first()

    @staticmethod
    def get_by_hash(hash_id, username=None):
        """Get a bmark from the system via the hash_id"""
        # normalize the url
        qry = Bmark.query.join(Bmark.hashed).\
            options(contains_eager(Bmark.hashed)).\
            filter(Hashed.hash_id == hash_id)

        if username:
            qry = qry.filter(Bmark.username == username)

        return qry.first()

    @staticmethod
    def find(limit=50, order_by=None, page=0, tags=None, username=None,
             with_content=False, with_tags=True, requested_by=None):
        """Search for specific sets of bookmarks"""
        qry = Bmark.query
        qry = qry.join(Bmark.hashed).\
            options(contains_eager(Bmark.hashed))

        offset = limit * page

        # If noqa is not used here the below error occurs with make lint.
        # comparison to False should be 'if cond is False:'
        # or 'if not cond:'
        if not requested_by:
            qry = qry.filter(Bmark.is_private == False)    # noqa
        elif requested_by != username:
            qry = qry.filter(Bmark.is_private == False)    # noqa

        if username:
            qry = qry.filter(Bmark.username == username)

        if order_by is None:
            order_by = Bmark.stored.desc()

        if not tags:
            qry = qry.order_by(order_by).\
                limit(limit).\
                offset(offset).\
                from_self()

        if tags:
            tags = [tag.lower() for tag in tags]  # For case matching
            qry = qry.join(Bmark.tags).\
                options(contains_eager(Bmark.tags))

            if isinstance(tags, str):
                qry = qry.filter(Tag.name == tags)
                qry = qry.order_by(order_by).\
                    limit(limit).\
                    offset(offset).\
                    from_self()
            else:
                if username:
                    good_filter = and_(
                        Bmark.bid == bmarks_tags.c.bmark_id,
                        Bmark.username == username
                    )
                else:
                    good_filter = (Bmark.bid == bmarks_tags.c.bmark_id)

                bids_we_want = select(
                    [bmarks_tags.c.bmark_id.label('good_bmark_id')],
                    from_obj=[
                        bmarks_tags.join(
                            'tags',
                            and_(
                                Tag.name.in_(tags),
                                bmarks_tags.c.tag_id == Tag.tid
                            )
                        ).
                        join('bmarks', good_filter)
                    ]).\
                    group_by(bmarks_tags.c.bmark_id, Bmark.stored).\
                    having(
                        func.count(bmarks_tags.c.tag_id) >= len(tags)
                    ).order_by(Bmark.stored.desc())

                qry = qry.join(
                    (
                        bids_we_want.limit(limit).offset(offset).alias('bids'),
                        Bmark.bid == bids_we_want.c.good_bmark_id
                    )
                )

        # now outer join with the tags again so that we have the
        # full list of tags for each bmark we filtered down to
        if with_tags:
            qry = qry.outerjoin(Bmark.tags).\
                options(contains_eager(Bmark.tags))

        if with_content:
            qry = qry.outerjoin(Bmark.readable).\
                options(contains_eager(Bmark.readable))

        qry = qry.options(joinedload('hashed'))
        return qry.order_by(order_by).all()

    @staticmethod
    def user_dump(username, requested_by):
        """Get a list of all of the user's bookmarks for an export dump usually

        """
        qry = Bmark.query.outerjoin(Bmark.tags).\
            options(
                contains_eager(Bmark.tags)
            ).\
            join(Bmark.hashed).\
            options(
                contains_eager(Bmark.hashed)
            ).\
            filter(Bmark.username == username)

        if requested_by != username:
            qry = qry.filter(Bmark.is_private == False)  # noqa

        qry = qry.order_by(Bmark.stored.desc())

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
                options(contains_eager(Hashed.bmark,
                                       bmark.tags,
                                       alias=tags))
        res = qry.all()
        return res

    @staticmethod
    def store(url, username, desc, ext, tags, dt=None, inserted_by=None,
              is_private=False):
        """Store a bookmark

        :param url: bookmarked url
        :param desc: the one line description
        :param ext: the extended description/notes
        :param dt: The original stored time of this bmark
        :param fulltext: an instance of a fulltext handler

        """
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            raise InvalidBookmark('The url provided is not valid: ' + url)

        mark = Bmark(
            url,
            username,
            desc=desc,
            ext=ext,
            tags=tags,
            is_private=is_private,
        )

        mark.inserted_by = inserted_by
        DBSession.add(mark)

        # if we have a dt then manually set the stored value
        if dt is not None:
            mark.stored = dt

        return mark

    @staticmethod
    def hash_list(username=None):
        """Get a list of the hash_ids we have stored"""
        qry = DBSession.query(Bmark.hash_id)

        if username:
            qry = qry.filter(Bmark.username == username)

        return qry.all()

    @staticmethod
    def count(username=None, distinct=False, distinct_users=False,
              is_private=False):
        """How many bookmarks are there

        :param username: should we limit to a username?

        """
        qry = DBSession.query(Bmark.hash_id)
        qry = qry.filter(Bmark.is_private == is_private)
        if username:
            qry = qry.filter(Bmark.username == username)
        if distinct:
            qry = qry.distinct()
        if distinct_users:
            qry = DBSession.query(Bmark.username).distinct()
        return qry.count()

    @staticmethod
    def delete_all_bookmarks(username):
        """Deletes all the bookmarks of the user

        :param username : The username of the logged-in user
        """
        bids = DBSession.query(Bmark.bid).\
            filter(Bmark.username == username).\
            all()
        if len(bids):
            deltags = bmarks_tags.delete().where(
                bmarks_tags.c.bmark_id.in_([i[0] for i in bids])
            )
            DBSession.execute(deltags)
            Bmark.query.filter(Bmark.username == username).delete()
            return len(bids)
        else:
            return None


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
        # url = url.strip().strip('/')
        return url


class Bmark(Base):
    """Basic bookmark table object"""
    __tablename__ = "bmarks"

    bid = Column(Integer, autoincrement=True, primary_key=True)
    hash_id = Column(Unicode(22), ForeignKey('url_hash.hash_id'))
    description = Column(UnicodeText())
    extended = Column(UnicodeText())
    stored = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.utcnow)
    clicks = Column(Integer, default=0)
    is_private = Column(Boolean, nullable=False, default=False)

    # this could be chrome_extension, firefox_extension, website, browser XX,
    # import, etc
    inserted_by = Column(Unicode(255))
    username = Column(Unicode(255), ForeignKey('users.username'),
                      nullable=False,)

    # DON"T USE
    tag_str = Column(UnicodeText())

    tags = relation(
        Tag,
        backref="bmark",
        collection_class=attribute_mapped_collection('name'),
        secondary=bmarks_tags,
        lazy='joined',
        innerjoin=False,
    )

    hashed = relation(Hashed,
                      backref="bmark",
                      uselist=False
                      )

    readable = relation(Readable,
                        backref="bmark",
                        cascade="all, delete, delete-orphan",
                        primaryjoin="Readable.bid == Bmark.bid",
                        uselist=False)

    def __init__(self, url, username, desc=None, ext=None, tags=None,
                 is_private=False):
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

        self.username = username
        self.description = desc
        self.extended = ext
        self.is_private = is_private

        # tags are space separated
        if tags:
            self.tags = TagMgr.from_string(tags)
        else:
            self.tags = {}

    def __str__(self):
        return "<Bmark: {0}:{1}>".format(self.bid, self.hashed.url)

    def tag_string(self):
        """Generate a single spaced string of our tags"""
        return u" ".join([tag for tag in self.tags.iterkeys()])

    def update_tags(self, tag_string):
        """Given a tag string, split and update our tags to be these"""
        self.tags = TagMgr.from_string(tag_string)

    def has_access(self, username):
        """Check if a user has access to view a bookmark"""
        if self.is_private:
            if self.username == username:
                return True
            elif username:
                logging.warning(username + " requested for " + self.username +
                                " bookmark")
            return False
        else:
            return True


def bmark_fulltext_tag_str_update(mapper, connection, target):
    """Update things before insert/update for fulltext needs"""
    target.tag_str = target.tag_string()

event.listen(Bmark, 'before_insert', bmark_fulltext_tag_str_update)
event.listen(Bmark, 'before_update', bmark_fulltext_tag_str_update)


def bmark_fulltext_insert_update(mapper, connection, target):
    """Update things before insert/update for the fulltext needs

    """
    content = u""
    if target.readable and target.readable.clean_content:
        content = target.readable.clean_content

    # Background the process of fulltext indexing this bookmark's content.
    from bookie.bcelery import tasks
    tasks.fulltext_index_bookmark.delay(target.bid, content)

event.listen(Bmark, 'after_insert', bmark_fulltext_insert_update)
event.listen(Bmark, 'after_update', bmark_fulltext_insert_update)

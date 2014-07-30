"""Generate some stats on the bookmarks in the syste

Stats we want to track

- total bookmarks per day
- total # of tags in the system per day
- unique...not sure

- per user - number of bookmarks they have that day

- the popularity tracking numbers...let's show most popular by clicks? not
really stats

- outstanding invites
- invites sent but not accepted

# do the users thing as an hourly job, but assign a letter per hour of the day
# and run it that way. on hour 0 run A users, on hour 1 run B users, on hour
# 23 run xzy users.

"""
from calendar import monthrange
from datetime import (
    datetime,
    timedelta,
)

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode

from bookie.models import Base
from bookie.models import DBSession
from bookie.models import BmarkMgr
from bookie.models import TagMgr
from bookie.models.queue import ImportQueueMgr


IMPORTER_CT = u'importer_queue'
TOTAL_CT = u'user_bookmarks'
UNIQUE_CT = u'unique_bookmarks'
TAG_CT = u'total_tags'
USER_CT = u'user_bookmarks_{0}'
STATS_WINDOW = 30


class StatBookmarkMgr(object):
    """Handle our agg stuff for the stats on bookmarks"""

    @staticmethod
    def get_stat(start, end, *stats):
        """Fetch the records from the stats table for these guys"""
        qry = StatBookmark.query
        qry = qry.filter(StatBookmark.tstamp > start)
        qry = qry.filter(StatBookmark.tstamp <= end)

        if stats:
            qry = qry.filter(StatBookmark.attrib.in_(stats))

        # order things up by their date so they're grouped together
        qry.order_by(StatBookmark.tstamp)
        return qry.all()

    @staticmethod
    def get_user_bmark_count(username, start_date, end_date):
        """Fetch the bookmark count for the user from the stats table"""
        qry = (StatBookmark.query.
               filter(StatBookmark.attrib == USER_CT.format(username)).
               filter(StatBookmark.tstamp >= start_date).
               filter(StatBookmark.tstamp <= end_date))

        # Order the result by their timestamp.
        qry = qry.order_by(StatBookmark.tstamp)
        return qry.all()

    @staticmethod
    def count_unique_bookmarks():
        """Count the unique number of bookmarks in the system"""
        total = BmarkMgr.count(distinct=True)
        stat = StatBookmark(attrib=UNIQUE_CT, data=total)
        DBSession.add(stat)

    @staticmethod
    def count_total_bookmarks():
        """Count the total number of bookmarks in the system"""
        total = BmarkMgr.count()
        stat = StatBookmark(attrib=TOTAL_CT, data=total)
        DBSession.add(stat)

    @staticmethod
    def count_total_tags():
        """Count the total number of tags in the system"""
        total = TagMgr.count()
        stat = StatBookmark(attrib=TAG_CT, data=total)
        DBSession.add(stat)

    @staticmethod
    def count_importer_depth():
        """Mark how deep the importer queue is at the moment"""
        total = ImportQueueMgr.size()
        stat = StatBookmark(attrib=IMPORTER_CT, data=total)
        DBSession.add(stat)

    @staticmethod
    def count_user_bookmarks(username):
        """Count the total number of bookmarks for the user in the system"""
        # We need a count of both public bookmarks and private bookmarks.
        total = BmarkMgr.count(username, is_private=False) + BmarkMgr.count(
            username, is_private=True)
        stat = StatBookmark(
            attrib=USER_CT.format(username),
            data=total
        )
        DBSession.add(stat)

    @staticmethod
    def count_user_bmarks(username, start_date=None, end_date=None):
        """Get a list of user bookmark count"""
        if start_date:
            start_date = start_date.split(' ')
            start_date = datetime.strptime(start_date[0], '%Y-%m-%d')
        if end_date:
            end_date = end_date.split(' ')
            end_date = datetime.strptime(end_date[0], '%Y-%m-%d')
        if not start_date:
            if not end_date:
                # If both start_date and end_date are None,
                # end_date will be the current date
                end_date = datetime.utcnow()

            # Otherwise if there's no start_date but we have an end_date,
            # assume that the user wants the STATS_WINDOW worth of stats.
            start_date = end_date - timedelta(days=STATS_WINDOW)
        elif start_date and not end_date:
            if start_date.day == 1:
                # If the starting day is 1, stats of the month is returned
                days = monthrange(start_date.year, start_date.day)[1] - 2
                end_date = start_date + timedelta(days=days)
            else:
                end_date = start_date + timedelta(days=STATS_WINDOW)
        # Since we're comparing dates with 00:00:00 we need to add one day and
        # do <=.
        return [
            StatBookmarkMgr.get_user_bmark_count(
                username, start_date, end_date + timedelta(days=1)),
            start_date,
            end_date
        ]


class StatBookmark(Base):
    """First stats we track are the counts of things.

    """
    __tablename__ = 'stats_bookmarks'

    id = Column(Integer, autoincrement=True, primary_key=True)
    tstamp = Column(DateTime, default=datetime.utcnow)
    attrib = Column(Unicode(100), nullable=False)
    data = Column(Integer, nullable=False, default=0)

    def __init__(self, **kwargs):
        self.attrib = kwargs.get('attrib', 'unknown')
        self.data = kwargs.get('data', 0)
        self.tstamp = kwargs.get('tstamp', datetime.utcnow())

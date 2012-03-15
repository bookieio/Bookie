from datetime import datetime
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Add the stats bookmark table"""
    meta = MetaData(migrate_engine)

    stats = Table('stats_bookmarks', meta,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('tstamp', DateTime, default=datetime.now),
        Column('attrib', Unicode(100), nullable=False),
        Column('data', Integer, nullable=False, default=0)
    )

    stats.create()


def downgrade(migrate_engine):
    """Bye stats bookmark table"""
    meta = MetaData(migrate_engine)
    stats = Table('stats_bookmarks', meta)
    stats.drop()

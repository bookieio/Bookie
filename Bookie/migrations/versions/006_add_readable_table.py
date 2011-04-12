from datetime import datetime
from sqlalchemy import *
from migrate import *


def get_table(engine):
    """Get the table def"""

    meta = MetaData(engine)
    readable = Table('readable', meta,
        Column('hash_id', Unicode(22), primary_key=True),
        Column('content', UnicodeText),
        Column('imported', DateTime, default=datetime.now),
    )

    return readable

def upgrade(migrate_engine):
    """setup the db for the readable table content"""
    readable = get_table(migrate_engine)
    readable.create()

def downgrade(migrate_engine):
    """And drop the table"""
    readable = get_table(migrate_engine)
    readable.drop


from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    """Add a clicks counter to the bmark table for that user

    will sync with the hashed clicks for overall clicks

    """
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)
    clicks = Column('clicks', Integer, nullable=False, server_default='0')
    create_column(clicks, bmarks)

def downgrade(migrate_engine):
    """Remove the new column"""
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)

    click_col = Column('clicks', Integer)
    drop_column(click_col, bmarks)

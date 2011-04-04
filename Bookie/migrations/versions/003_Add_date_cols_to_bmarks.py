from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Store a datetime for when a bookmark is saved and changed"""
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)

    stored = Column('stored', DateTime)
    updated = Column('updated', DateTime)

    create_column(stored, bmarks)
    create_column(updated, bmarks)


def downgrade(migrate_engine):
    """And drop the two new columns"""
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)

    stored = Column('stored', DateTime)
    updated = Column('updated', DateTime)

    drop_column(stored, bmarks)
    drop_column(updated, bmarks)

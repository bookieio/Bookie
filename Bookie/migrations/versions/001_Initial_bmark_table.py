from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Define the original base bmark table"""
    meta = MetaData(migrate_engine)

    b_table = Table('bmarks', meta,
        Column('bid', Integer, autoincrement=True, primary_key=True),
        Column('url', UnicodeText()),
        Column('description', UnicodeText()),
        Column('extended', UnicodeText()),
    )

    b_table.create()


def downgrade(migrate_engine):
    """Obviously, drop said table"""
    meta = MetaData(migrate_engine)

    b_table = Table('bmarks', meta)
    b_table.drop()

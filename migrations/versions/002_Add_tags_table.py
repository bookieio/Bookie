from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Add the tags table and the assoc table for bmarks"""
    meta = MetaData(migrate_engine)

    t_table = Table('tags', meta,
        Column('tid', Integer, autoincrement=True, primary_key=True),
        Column('name', Unicode(255), unique=True ),
    )

    ta_table = Table('bmark_tags', meta,
        Column('bmark_id', Integer, primary_key=True),
        Column('tag_id', Integer, primary_key=True),
    )

    t_table.create()
    ta_table.create()


def downgrade(migrate_engine):
    """And drop them away"""
    meta = MetaData(migrate_engine)

    t_table = Table('tags', meta)
    ta_table = Table('bmark_tags', meta)

    t_table.drop()
    ta_table.drop()

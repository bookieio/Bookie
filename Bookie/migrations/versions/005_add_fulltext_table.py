from sqlalchemy import *
from migrate import *


def for_sqlite(engine):
    """Add the table structure for sqlite db"""
    sql = """CREATE VIRTUAL TABLE fulltext USING fts3(bid, description, extended, tags);"""
    engine.execute(sql)


def drop_sqlite(engine):
    """The downgrade method for sqlite"""
    sql = """DROP TABLE fulltext"""
    engine.execute(sql)


def upgrade(migrate_engine):
    """Right now this is sqlite specific

    Eventually we'll need to detect the db type based on the engine and call
    the correct method to add the right table structure.

    The idea is to allow searching on the desc, extended, tags (as words)

    I would like to do the url as well, but not sure how to tokenize it.
    e.g. engadget would come up with a search for gadget

    """
    for_sqlite(migrate_engine)


def downgrade(migrate_engine):
    """And destroy the tables created"""
    drop_sqlite(migrate_engine)


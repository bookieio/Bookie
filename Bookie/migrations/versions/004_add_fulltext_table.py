from sqlalchemy import *
from migrate import *


def for_sqlite(engine):
    """Add the table structure for sqlite db"""
    sql = """CREATE VIRTUAL TABLE fulltext USING fts3(bid, description, extended, tag_string);"""
    engine.execute(sql)


def drop_sqlite(engine):
    """The downgrade method for sqlite"""
    sql = """DROP TABLE fulltext"""
    engine.execute(sql)


def for_mysql(engine):
    """Add the table structure for mysql db"""
    meta = MetaData(engine)
    bmarks = Table('bmarks', meta, autoload=True)

    tag_str = Column('tag_string', UnicodeText())
    tag_str.create(bmarks)

    # add the fulltext index

    ft_index = """ALTER TABLE  `bmarks`
                      ADD FULLTEXT `fulltext`
                        (`description` , `extended`, `tag_string`);
    """
    engine.execute(ft_index)


def drop_mysql(engine):
    """The downgrade method for mysql"""
    meta = MetaData(engine)
    bmarks = Table('bmarks', meta, autoload=True)
    tag_str = Column('tag_string', UnicodeText())
    drop_column(bmarks, tag_str)

    engine.execute("ALTER TABLE bmarks DROP INDEX `fulltext`;")

def upgrade(migrate_engine):
    """Right now this is sqlite specific

    Eventually we'll need to detect the db type based on the engine and call
    the correct method to add the right table structure.

    The idea is to allow searching on the desc, extended, tags (as words)

    I would like to do the url as well, but not sure how to tokenize it.
    e.g. engadget would come up with a search for gadget

    """
    if 'sqlite' in migrate_engine.dialect.driver.lower():
        for_sqlite(migrate_engine)

    elif 'mysql' in migrate_engine.dialect.driver.lower():
        for_mysql(migrate_engine)


def downgrade(migrate_engine):
    """And destroy the tables created"""
    # drop_sqlite(migrate_engine)
    print migrate_engine.dialect

    # for_sqlite(migrate_engine)
    pass


    pass


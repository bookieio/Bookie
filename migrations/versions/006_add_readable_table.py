from datetime import datetime
from sqlalchemy import *
from migrate import *

def for_sqlite(engine):
    """Add the table structure for sqlite db"""
    sql = """CREATE VIRTUAL TABLE readable_fts USING fts3(hash_id, content);"""
    engine.execute(sql)


def drop_sqlite(engine):
    """The downgrade method for sqlite"""
    sql = """DROP TABLE readable_fts"""
    engine.execute(sql)


def for_mysql(engine):
    """Add the table structure for mysql db"""
    # add the fulltext index
    ft_index = """ALTER TABLE `readable`
                      ADD FULLTEXT `readable_fts`
                        (`content`);
    """
    engine.execute(ft_index)


def drop_mysql(engine):
    """The downgrade method for mysql"""
    engine.execute("ALTER TABLE readable DROP INDEX `readable_fts`;")


def for_pgsql(engine):
    """Postgres we're going to start with the slowest, but easiest option"""
    idx_sql = [
        "CREATE INDEX content_ftidx ON readable USING gin(to_tsvector('english', content));",
    ]

    for sql in idx_sql:
        engine.execute(sql)


def drop_pgsql(engine):
    """Postgres, drop the indexes in question"""
    engine.execute("ALTER TABLE readable DROP INDEX content_ftidx;")


def get_table(engine):
    """Get the table def"""

    meta = MetaData(engine)
    readable = Table('readable', meta,
        Column('hash_id', Unicode(22), primary_key=True),
        Column('content', UnicodeText),
        Column('imported', DateTime, default=datetime.now),
        Column('content_type', Unicode(255)),
        Column('status_code', Integer),
        Column('status_message', Unicode(255)),
    )

    return readable

def upgrade(migrate_engine):
    """setup the db for the readable table content"""
    readable = get_table(migrate_engine)
    readable.create()

    # now do some db specific modifications for how they support fulltext
    if 'sqlite' in migrate_engine.dialect.driver.lower():
        for_sqlite(migrate_engine)

    elif 'mysql' in migrate_engine.dialect.driver.lower():
        for_mysql(migrate_engine)

    elif 'pg' in migrate_engine.dialect.driver.lower():
        # currently psycopg2
        for_pgsql(migrate_engine)


def downgrade(migrate_engine):
    """And drop the table

    """
    if 'sqlite' in migrate_engine.dialect.driver.lower():
        drop_sqlite(migrate_engine)

    elif 'mysql' in migrate_engine.dialect.driver.lower():
        drop_mysql(migrate_engine)

    elif 'pg' in migrate_engine.dialect.driver.lower():
        drop_pgsql(migrate_engine)

    readable = get_table(migrate_engine)
    readable.drop()

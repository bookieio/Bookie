import os
from BeautifulSoup import BeautifulSoup
from sqlalchemy import *
from sqlalchemy.exc import ProgrammingError
from migrate import *

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
from whoosh.index import create_in
from whoosh.index import open_dir


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
    # add the fulltext index
    ft_index = """ALTER TABLE  `bmarks`
                      ADD FULLTEXT `fulltext`
                        (`description` , `extended`, `tag_str`);
    """
    engine.execute(ft_index)


def drop_mysql(engine):
    """The downgrade method for mysql"""
    engine.execute("ALTER TABLE bmarks DROP INDEX `fulltext`;")


def for_pgsql(engine):
    """Postgres we're going to start with the slowest, but easiest option"""
    idx_sql = [
        "CREATE INDEX desc_ftidx ON bmarks USING gin(to_tsvector('english', description));",
        "CREATE INDEX ext_ftidx ON bmarks USING gin(to_tsvector('english', extended));",
        "CREATE INDEX tag_ftidx ON bmarks USING gin(to_tsvector('english', tag_str));",
    ]

    for sql in idx_sql:
        engine.execute(sql)


def drop_pgsql(engine):
    """Postgres, drop the indexes in question"""
    try:
        engine.execute("DROP INDEX desc_ftidx;")
        engine.execute("DROP INDEX tag_ftidx;")
    except ProgrammingError:
        # if the indexes are gone oh well
        pass


def run_whoosh_index(engine):
    """Build the whoosh index from anything in the db currently"""
    meta = MetaData(engine)

    class BmarkSchema(SchemaClass):
        bid = ID(stored=True)
        description = TEXT
        extended = TEXT
        tags = KEYWORD
        readable = TEXT(analyzer=StemmingAnalyzer())

    INDEX_NAME = 'bookie_index'
    if not os.path.exists(INDEX_NAME):
        os.mkdir(INDEX_NAME)
        WIX = create_in(INDEX_NAME, BmarkSchema)
    else:
        WIX = open_dir(INDEX_NAME)

    def get_writer():
        writer = WIX.writer()
        return writer

    writer = get_writer()

    bmarks = Table('bmarks', meta, autoload=True)
    readable = Table('readable', meta, autoload=True)
    b = select([bmarks])
    r = select([readable])

    all_b = engine.execute(b)
    all_r = engine.execute(r)

    ordered_r = dict([(r.hash_id, r) for r in all_r])

    for b in all_b:
        r = u' '.join(BeautifulSoup(ordered_r[b['hash_id']]['content']).findAll(text=True)) if (b['hash_id'] in ordered_r and ordered_r[b['hash_id']]['content'] is not None) else u''

        writer.add_document(
            bid=unicode(b['bid']),
            description=b['description'] if b['description'] else u"",
            extended=b['extended'] if b['extended'] else u"",
            tags=b['tag_str'] if b['tag_str'] else u"",
            readable=r
        )
    writer.commit()


def upgrade(migrate_engine):
    """Destroy all the fulltext indexes/code since we're moving to whoosh"""

    if 'sqlite' in migrate_engine.dialect.driver.lower():
        drop_sqlite(migrate_engine)

    elif 'mysql' in migrate_engine.dialect.driver.lower():
        drop_mysql(migrate_engine)

    elif 'pg' in migrate_engine.dialect.driver.lower():
        drop_pgsql(migrate_engine)

    run_whoosh_index(migrate_engine)


def downgrade(migrate_engine):
    """ A downgrade means putting the indexes back

    The idea is to allow searching on the desc, extended, tags (as words)

    I would like to do the url as well, but not sure how to tokenize it.
    e.g. engadget would come up with a search for gadget

    """
    # now do some db specific modifications for how they support fulltext
    if 'sqlite' in migrate_engine.dialect.driver.lower():
        for_sqlite(migrate_engine)

    elif 'mysql' in migrate_engine.dialect.driver.lower():
        for_mysql(migrate_engine)

    elif 'pg' in migrate_engine.dialect.driver.lower():
        # currently psycopg2
        for_pgsql(migrate_engine)

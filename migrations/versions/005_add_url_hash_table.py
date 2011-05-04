"""Add url hash table

This feature is meant to store the urls in a seperate table and provide a short
url hash for them. 

This table will also be used to store some metadata about the urls. We want to
use the hash to provide a redirect service within bookie. During redirection
we'll keep track of the click and store a popularity counter in the table. 

This will allow us to provide a 'popular' view down the road.

When we get multi-user support into play, the hash table will be the single
place to store urls and will let us grab other people's tags/etc they stored
with as suggested tags and such.

"""

import shortuuid
from sqlalchemy import *
from sqlalchemy import exc
from migrate import *


def get_url_hash(engine):
    """Generate the url hash table"""
    meta = MetaData(engine)

    hash_table = Table('url_hash', meta,
        Column('hash_id', Unicode(22), primary_key=True),
        Column('url', UnicodeText()),
        Column('clicks', Integer),
    )

    return hash_table


def hash_urls(engine, hash_table, bmarks):
    """Get all of the bmarks in the system and hash the urls into url_hash"""
    conn = engine.connect()
    sel_set = select([bmarks.c.url])
    res = conn.execute(sel_set)

    if res.rowcount > 0:
        hash_ins = hash_table.insert()
        values = []
        for bmk in res:
            print "Outputting: " + bmk['url']
            new_dat = {'url': bmk['url'],
                       'hash_id': shortuuid.uuid(url=str(bmk['url'])),
                       'clicks': 0}
            values.append(new_dat)

            # now we also need to add that hashid to the bmarks table
            conn.execute(bmarks.update().\
                                values(hash_id=new_dat['hash_id']).\
                                where(bmarks.c.url==new_dat['url']))

        # mass insert into the hash table
        conn.execute(hash_ins, values)


def restore_urls(engine, hash_table, bmarks):
    """Go through all of the hash values and store the original urls"""
    conn = engine.connect()

    sel_set = select([hash_table.c.url, hash_table.c.hash_id])
    res = conn.execute(sel_set)

    for hashed in res:
        conn.execute(bmarks.update().\
                            values(url=hashed['url']).\
                            where(bmarks.c.hash_id==hashed['hash_id']))


def upgrade(migrate_engine):
    """Upgrade is a several step process to keep tings together

    - First we need to create the new url_hash table
    - Then we need to add a new url_hash field in the bmarks table
    - Next we need to go through and hash the current urls in the system and
      populate the hash table while adding the hash into the bmarks table
    - finally we can drop the url column from the bmarks table

    """
    hash_tbl = get_url_hash(migrate_engine)
    hash_tbl.create()

    # now add a hash column to the bmarks table
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)
    hash_id = Column('hash_id', Unicode(22))
    create_column(hash_id, bmarks)

    hash_urls(migrate_engine, hash_tbl, bmarks)

    url_col = Column('url', UnicodeText())
    drop_column(url_col, bmarks)


def downgrade(migrate_engine):
    """To downgrade we'll need to reverse the steps

    - Create the url column on bmarks
    - copy over all of the original url strings from the hash table
    - drop the hash id column on the bmarks table
    - drop the hash table

    """
    hash_tbl = get_url_hash(migrate_engine)

    # now add a hash column to the bmarks table
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)
    url = Column('url', UnicodeText)

    try:
        create_column(url, bmarks)
    except exc.OperationalError:
        # we get an eception with sqlite because you can't drop columns
        # so the url column never went away
        # and here we're trying to add it again
        pass

    restore_urls(migrate_engine, hash_tbl, bmarks)

    # now we can drop the table
    hash_tbl.drop()

    # and the tied column
    hash_col = Column('hash_id', Unicode(22))
    drop_column(hash_col, bmarks)



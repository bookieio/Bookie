from sqlalchemy import *
from migrate import *
import hashlib


def generate_hash(url_string):
    m = hashlib.sha256()
    m.update(url_string)
    return m.hexdigest()[:14]


def upgrade(migrate_engine):
    """We've changed the algo for hashing and need to update all hash_id

    The hash function is copied to this migration in case we need to change it
    later on. We need to loop through each url in url_hash, generate a new
    hash, and then update the matching hashes in:

        url_hash
        bmarks
        readable
        -- if sqlite -- readable_fts
    """
    meta = MetaData(migrate_engine)

    # get the list of all urls from url_hash table
    url_hash = Table('url_hash', meta, autoload=True)
    bmarks = Table('bmarks', meta, autoload=True)
    readable = Table('readable', meta, autoload=True)

    if 'sqlite' in migrate_engine.dialect.driver.lower():
        readable_fts = Table('readable', meta, autoload=True)
    else:
        readable_fts = None

    hashes = migrate_engine.execute(select([url_hash]))

    for orig in hashes:
        orig_hash = orig['hash_id']
        new_hash = generate_hash(orig_hash)

        up_bmarks = bmarks.update().where(bmarks.c.hash_id==orig_hash).values(hash_id=new_hash)
        up_url_hash = url_hash.update().where(url_hash.c.hash_id==orig_hash).values(hash_id=new_hash)
        up_readable = readable.update().where(readable.c.hash_id==orig_hash).values(hash_id=new_hash)

        migrate_engine.execute(up_bmarks)
        migrate_engine.execute(up_url_hash)
        migrate_engine.execute(up_readable)

        if readable_fts is not None:
            migrate_engine.execute(
                readable_fts.update().\
                             where(readable_fts.c.hash_id==orig_hash).\
                             values(hash_id=new_hash))


def downgrade(migrate_engine):
    """We're not downgrading. It requires adding back the uuid package to be
    able to re-calc the old hash_id. If you need to downgrade you can do it
    manually by basically copying the above and instead of generate_hash you
    use the shortuuid package to generate a hash"""
    pass

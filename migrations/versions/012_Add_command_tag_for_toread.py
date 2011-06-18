from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    """Need to add a new tag we can use via commands !toread, toread"""
    meta = MetaData(migrate_engine)

    tags = Table('tags', meta, autoload=True)

    migrate_engine.execute(tags.insert().\
                           values(name='toread'))

def downgrade(migrate_engine):
    """And remove that tag"""
    meta = MetaData(migrate_engine)
    tags = Table('tags', meta, autoload=True)
    migrate_engine.execute(tags.delete().\
                           where(name='toread'))


from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    """Add the username field to the bmarks table"""
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)

    # we can't have nullable at first, we need to set the values
    username = Column('username', Unicode(255))
    create_column(username, bmarks)

    # all current bookmarks need to be owned by 'admin' our default user
    migrate_engine.execute(bmarks.update().values(username=u'admin'))

    # now we add on the nullable=False
    alter_column('username', nullable=False, table=bmarks)

def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)
    username = Column('username', Unicode(255), nullable=False)

    drop_column(username, bmarks)


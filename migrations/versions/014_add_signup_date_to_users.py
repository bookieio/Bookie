from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    users = Table('users', meta, autoload=True)
    signup = Column('signup', DateTime)
    create_column(signup, users)


def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)

    users = Table('users', meta, autoload=True)
    signup = Column('signup', DateTime)

    drop_column(signup, users)

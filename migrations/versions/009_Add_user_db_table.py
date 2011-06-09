from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    """Add the users table we'll use """
    meta = MetaData(migrate_engine)
    user = Table('users', meta,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('username', Unicode(255), unique=True),
        Column('password', Unicode(60)),
        Column('email', Unicode(255), unique=True),
        Column('activated', Boolean, server_default="0"),
        Column('is_admin', Boolean, server_default="0"),
        Column('last_login', DateTime, server_default=func.now()),
    )

    user.create()

def downgrade(migrate_engine):
    """And the big drop"""
    meta = MetaData(migrate_engine)
    user = Table('users', meta)
    user.drop()

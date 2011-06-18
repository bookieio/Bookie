from sqlalchemy import *
from migrate import *
from bookie.models.auth import User

def upgrade(migrate_engine):
    """Need to add a col to the users for their api key"""
    meta = MetaData(migrate_engine)

    users = Table('users', meta, autoload=True)
    api_key = Column('api_key', Unicode(12))
    create_column(api_key, users)

    # now add an api key for our admin user
    migrate_engine.execute(users.update().\
                           where(users.c.username==u'admin').\
                           values(api_key=User.gen_api_key()))


def downgrade(migrate_engine):
    """And bye bye api key column"""
    meta = MetaData(migrate_engine)

    users = Table('users', meta, autoload=True)
    api_key = Column('api_key', Unicode(12))

    drop_column(api_key, users)

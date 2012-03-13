from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    user = Table('users', meta, autoload=True)
    invite_ct = Column('invite_ct', Integer)
    invited_by = Column('invited_by', Unicode(255))

    create_column(invite_ct, user)
    create_column(invited_by, user)


def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)

    user = Table('users', meta, autoload=True)
    invite_ct = Column('invite_ct', Integer)
    invited_by = Column('invited_by', Unicode(255))

    drop_column(invite_ct, user)
    drop_column(invited_by, user)

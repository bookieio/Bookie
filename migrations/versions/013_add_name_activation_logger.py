from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(migrate_engine)

    # add the name column to the user table which we'll put into the account
    # view
    users = Table('users', meta, autoload=True)
    name = Column('name', Unicode(255))
    create_column(name, users)

    # add a table for activations, we need to be able to store validation keys
    # with timeouts so that we can reset/activate user accounts
    # is_active would be false and we'd check for a key and if that key is
    # still valid here
    activations = Table('activations', meta,
        Column('id', Integer, primary_key=True),
        Column('code', Unicode(60)),
        Column('valid_until', DateTime),
        Column('created_by', Unicode(255)),
    )

    activations.create()

    # we also want to start adding some logging information, eventually we'll
    # want this out of the db, but for now, let's log it and we'll work on
    # making this better later
    logging = Table('logging', meta,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('user', Unicode(255), nullable=False),
        Column('component', Unicode(50), nullable=False),
        Column('status', Unicode(10), nullable=False),
        Column('message', Unicode(255), nullable=False),
        Column('payload', UnicodeText),
        Column('tstamp', DateTime),
    )
    logging.create()


def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)

    users = Table('users', meta, autoload=True)
    name = Column('name', Unicode(255))

    drop_column(name, users)

    activations = Table('activations', meta)
    activations.drop()
    logging = Table('logging', meta)
    logging.drop()

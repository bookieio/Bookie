from datetime import datetime
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Add the importer table"""
    meta = MetaData(migrate_engine)

    importer = Table('import_queue', meta,
        Column('id', Integer, autoincrement=True, primary_key=True),
        Column('username', Unicode(255)),
        Column('file_path', Unicode(100), nullable=False),
        Column('tstamp', DateTime, default=datetime.now),
        Column('status', Integer),
        Column('completed', DateTime),
    )
    importer.create()


def downgrade(migrate_engine):
    """Bye importer table"""
    meta = MetaData(migrate_engine)
    stats = Table('import_queue', meta)
    stats.drop()

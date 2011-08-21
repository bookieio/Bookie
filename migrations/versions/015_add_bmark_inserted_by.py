from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    meta = MetaData(migrate_engine)
    bmarks = Table('bmarks', meta, autoload=True)
    inserted_by = Column('inserted_by', Unicode(255))
    create_column(inserted_by, bmarks)


def downgrade(migrate_engine):
    meta = MetaData(migrate_engine)

    bmarks = Table('bmarks', meta, autoload=True)
    inserted_by = Column('inserted_by', Unicode(255))

    drop_column(inserted_by, bmarks)

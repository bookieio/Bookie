from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """By default start all installs out with a bookmark to bmark.us

    It's cheesy, but helps with testing to have some base data and is good for
    pubbing the links

    """
    pass
    # from datetime import datetime
    # import transaction
    # from bookie.models import initialize_sql

    # initialize_sql(migrate_engine)

    # from bookie.models import DBSession
    # from bookie.models import Bmark

    # bmark_us = Bmark('http://bmark/us',
    #                  desc="Bookie Website",
    #                  ext= "Bookie Documentation Home",
    #                  tags = "bookmarks")

    # bmark_us.stored = datetime.now()
    # bmark_us.updated = datetime.now()
    # DBSession.add(bmark_us)
    # DBSession.flush()
    # transaction.commit()


def downgrade(migrate_engine):
    """We're not dropping this"""
    pass

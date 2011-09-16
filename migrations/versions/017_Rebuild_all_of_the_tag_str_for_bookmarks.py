from collections import defaultdict
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    """Walk through all bookmarks and reset the tag_str field"""
    meta = MetaData(migrate_engine)
    engine = migrate_engine
    bmarks = Table('bmarks', meta, autoload=True)
    tags = Table('tags', meta, autoload=True)
    btags = Table('bmark_tags', meta, autoload=True)

    b = select([bmarks, btags, tags]).where(bmarks.c.bid==btags.c.bmark_id).\
               where(btags.c.tag_id==tags.c.tid)
    all_b = engine.execute(b)

    summary = defaultdict(list)
    for b in all_b:
        print dict(b)
        print "\n"
        summary[b['bid']].append(b['name'])

    for key, tags in summary.items():
        print key, tags
        engine.execute(bmarks.update().values(tag_str=" ".join(tags)).where(bmarks.c.bid==key))


def downgrade(migrate_engine):
    """No valid undo here, so just pass"""
    pass

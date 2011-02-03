from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)

increment_tag_counter = """CREATE TRIGGER increment_tag_counter 
    AFTER INSERT ON bookmarks_tags
        BEGIN
            UPDATE tags SET count=(count + 1) WHERE id=new.tag_id;
        END;
"""

decrement_tag_counter = """CREATE TRIGGER decrement_tag_counter 
    AFTER DELETE ON bookmarks_tags
        BEGIN
            UPDATE tags SET count=(count - 1) WHERE id=old.tag_id;
        END;
"""


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    migrate_engine.execute(increment_tag_counter)
    migrate_engine.execute(decrement_tag_counter)

def downgrade():
    # Operations to reverse the above upgrade go here.
    migrate_engine.execute("DROP increment_tag_counter")
    migrate_engine.execute("DROP decrement_tag_counter")

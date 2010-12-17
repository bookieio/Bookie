from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)

tables = [
    Table('users', meta,
                Column('id', Integer, primary_key=True),
                Column('username', Unicode(255)),
                Column('email', Unicode(255)),
                Column('salt', Unicode(10))
                ),

    Table('bookmarks', meta,
                Column('id', Integer, primary_key=True),
                Column('hash', Unicode(40), unique=True),
                Column('url', UnicodeText()),
                Column('added', DateTime),
                Column('updated', DateTime)
                ),

    Table('tags', meta,
                Column('id', Integer, primary_key=True),
                Column('name', Unicode(50)),
                Column('count', Integer())
                ),

    Table('bookmarks_tags', meta,
                Column('bookmark_id', Integer(), primary_key=True),
                Column('tag_id', Integer(), primary_key=True)
                ),

    Table('users_tags', meta,
                Column('user_id', Integer(), primary_key=True),
                Column('tag_id', Integer(), primary_key=True),
                Column('tag_count', Integer())
                ),

    Table('users_bookmarks', meta,
                Column('user_id', Integer, primary_key=True),
                Column('bookmark_id', Integer, primary_key=True),
                Column('notes', UnicodeText()),
                Column('title', UnicodeText()),
                ),
]
                    

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    for table in tables:
        table.create()


def downgrade():
    # Operations to reverse the above upgrade go here.
    for table in tables:
        table.drop()

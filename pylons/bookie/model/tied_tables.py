from bookie_app import model
from bookie_app.model import meta
from sqlalchemy import Table, Column, Integer, ForeignKey

# tied table used to associate the Bookmark to the Tag models
bookmark_tags_table = Table('bookmarks_tags', meta.metadata,
        Column('bookmark_id', Integer, ForeignKey('bookmarks.id')),
        Column('tag_id', Integer, ForeignKey('tags.id')),
    )


# This is the association table for the many-to-many relationship between
# groups and permissions.
group_permission_table = Table('group_permission', meta.Base.metadata,
    Column('group_id', Integer, 
        ForeignKey('group.group_id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, 
        ForeignKey('permission.permission_id', onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships.
user_group_table = Table('user_group', meta.Base.metadata,
    Column('user_id', Integer, ForeignKey('user.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('group.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

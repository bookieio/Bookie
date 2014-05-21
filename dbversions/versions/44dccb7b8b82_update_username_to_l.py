"""update username to lowercase

Revision ID: 44dccb7b8b82
Revises: 9f274a38d84
Create Date: 2014-02-27 00:55:59.913206

"""

# revision identifiers, used by Alembic.
revision = '44dccb7b8b82'
down_revision = '9f274a38d84'

from alembic import op
import sqlalchemy as sa


def upgrade():
    connection = op.get_bind()
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    users = sa.Table('users', meta, autoload=True)
    bmarks = sa.Table('bmarks', meta, autoload=True)

    try:
        op.drop_constraint("bmarks_username_fkey", "bmarks")
        print 'dropped constraint'
    except (sa.exc.OperationalError, NotImplementedError) as exc:
        # If it's not supported then pass
        pass

    sel = sa.select([users])
    for user in connection.execute(sel):
        print 'updating for user: ' + user['username']
        lowered = sa.func.lower(user['username'])

        stmt = users.update().\
            where(users.c.username == user['username']).\
            values(username=lowered)
        connection.execute(stmt)

        stmt = bmarks.update().\
            where(bmarks.c.username == user['username']).\
            values(username=lowered)
        connection.execute(stmt)
        print 'done user: ' + user['username']

    try:
        op.create_foreign_key(
            "bmarks_username_fkey", "bmarks",
            "users", ["username"], ["username"])

        print 'added constraint'
    except (sa.exc.OperationalError, NotImplementedError) as exc:
        # If it's not supported then pass
        pass


def downgrade():
    pass

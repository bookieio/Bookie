"""add private bookmark support to bmarks table

Revision ID: 11087341e403
Revises: 44dccb7b8b82
Create Date: 2014-05-23 07:18:38.743431

"""

# revision identifiers, used by Alembic.
revision = '11087341e403'
down_revision = '44dccb7b8b82'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('bmarks', sa.Column('is_private', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()))
    # Update the existing bookmarks to be public.
    connection = op.get_bind()
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    bmarks = sa.Table('bmarks', meta, autoload=True)
    sel = sa.select([bmarks])
    stmt = bmarks.update().\
        values(is_private=False)
    connection.execute(stmt)


def downgrade():
    try:
        op.drop_column('bmarks', 'is_private')
    except sa.exc.OperationalError as exc:
        pass

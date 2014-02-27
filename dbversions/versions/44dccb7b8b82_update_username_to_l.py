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
    stmt = users.update().\
	   values(username=sa.func.lower(users.c.username))
    connection.execute(stmt)

def downgrade():
    pass

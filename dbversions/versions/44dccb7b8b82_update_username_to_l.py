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
    # the database update code goes here
    pass


def downgrade():
    pass

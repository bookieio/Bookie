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
    connection.execute("update users set username = 
		    subquery.newusername from (select id, lower(username)
		    as newusername from users) as subquery where users.id = subquery.id",
		    execution_options = None)


def downgrade():
    pass

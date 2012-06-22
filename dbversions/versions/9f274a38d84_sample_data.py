"""

Revision ID: 9f274a38d84
Revises: 5920b225d05d
Create Date: 2012-06-19 21:02:38.320088

"""

# revision identifiers, used by Alembic.
revision = '9f274a38d84'
down_revision = '5920b225d05d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Preseed data into the system."""
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    user = sa.Table('users', meta, autoload=True)

    # Add the initial admin user account.
    op.bulk_insert(user, [{
        'username': u'admin',
        'password': u'$2a$10$LoSEVbN6833RtwbGQlMhJOROgkjHNH4gjmzkLrIxOX1xLXNvaKFyW',
        'email': u'testing@dummy.com',
        'activated': True,
        'is_admin': True,
        'api_key': u'123456',
        }
    ])


def downgrade():
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    user = sa.Table('users', meta, autoload=True)

    # remove all records to undo the preseed.
    op.execute(user.delete())

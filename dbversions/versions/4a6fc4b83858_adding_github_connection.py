"""adding github connection

Revision ID: 4a6fc4b83858
Revises: dbc7a0f1182
Create Date: 2014-12-19 21:50:21.234299

"""

# revision identifiers, used by Alembic.
revision = '4a6fc4b83858'
down_revision = 'dbc7a0f1182'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('GithubConnection',
    sa.Column('connection_id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.Unicode(255), nullable=True),
    sa.Column('access_token', sa.Unicode(255), nullable=True),
    sa.Column('github_username', sa.Unicode(255), nullable=True),
    sa.Column('refresh_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(
        ['connection_id'], ['BaseConnection.id'],
        name="githubconnection_connectionid_fkey"),
    sa.PrimaryKeyConstraint('connection_id')
    )


def downgrade():
    op.drop_table('GithubConnection')

"""adding last_twitter_seen column

Revision ID: dbc7a0f1182
Revises: 352bb5f4fff9
Create Date: 2014-07-06 21:23:56.002719

"""

# revision identifiers, used by Alembic.
revision = 'dbc7a0f1182'
down_revision = '352bb5f4fff9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('TwitterConnection', sa.Column('last_tweet_seen', sa.Unicode(length=255), nullable=True))


def downgrade():
    op.drop_column('TwitterConnection', 'last_tweet_seen')

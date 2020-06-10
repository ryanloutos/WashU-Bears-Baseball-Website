"""Merge points 72ca94739b34, 81a651b50603, 941b3e7ebe30.

Revision ID: 488cd192c16b
Revises: 941b3e7ebe30, 81a651b50603, 72ca94739b34
Create Date: 2020-06-10 00:24:21.296596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '488cd192c16b'
down_revision = ('941b3e7ebe30', '81a651b50603', '72ca94739b34')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

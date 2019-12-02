"""Added admin ability

Revision ID: 515163227457
Revises: 1004ac713339
Create Date: 2019-12-02 13:37:37.743898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '515163227457'
down_revision = '1004ac713339'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('admin', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_user_admin'), 'user', ['admin'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_admin'), table_name='user')
    op.drop_column('user', 'admin')
    # ### end Alembic commands ###

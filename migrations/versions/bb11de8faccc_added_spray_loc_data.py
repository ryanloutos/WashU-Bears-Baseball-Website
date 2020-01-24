"""added spray/loc data

Revision ID: bb11de8faccc
Revises: 6aa604f63472
Create Date: 2020-01-23 15:54:48.714318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb11de8faccc'
down_revision = '6aa604f63472'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pitch', sa.Column('loc_x', sa.Float(), nullable=True))
    op.add_column('pitch', sa.Column('loc_y', sa.Float(), nullable=True))
    op.add_column('pitch', sa.Column('spray_x', sa.Float(), nullable=True))
    op.add_column('pitch', sa.Column('spray_y', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pitch', 'spray_y')
    op.drop_column('pitch', 'spray_x')
    op.drop_column('pitch', 'loc_y')
    op.drop_column('pitch', 'loc_x')
    # ### end Alembic commands ###
"""empty message

Revision ID: 6e27f55f5732
Revises: c0090f308707
Create Date: 2020-01-17 17:42:09.434072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e27f55f5732'
down_revision = 'c0090f308707'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('outing') as batch_op:
        batch_op.drop_index('ix_outing_pitcher_id')
        batch_op.drop_column('pitcher_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('outing', sa.Column('pitcher_id', sa.INTEGER(), nullable=True))
    op.create_index('ix_outing_pitcher_id', 'outing', ['pitcher_id'], unique=False)
    # ### end Alembic commands ###

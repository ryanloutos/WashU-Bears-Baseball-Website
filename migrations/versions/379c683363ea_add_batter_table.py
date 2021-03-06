"""add Batter table

Revision ID: 379c683363ea
Revises: 492b04a12351
Create Date: 2019-12-19 19:49:50.221250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '379c683363ea'
down_revision = '492b04a12351'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('short_name', sa.String(length=8), nullable=True),
    sa.Column('bats', sa.String(length=8), nullable=True),
    sa.Column('opponent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['opponent_id'], ['opponent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_batter_bats'), 'batter', ['bats'], unique=False)
    op.create_index(op.f('ix_batter_name'), 'batter', ['name'], unique=False)
    op.create_index(op.f('ix_batter_opponent_id'), 'batter', ['opponent_id'], unique=False)
    op.create_index(op.f('ix_batter_short_name'), 'batter', ['short_name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_batter_short_name'), table_name='batter')
    op.drop_index(op.f('ix_batter_opponent_id'), table_name='batter')
    op.drop_index(op.f('ix_batter_name'), table_name='batter')
    op.drop_index(op.f('ix_batter_bats'), table_name='batter')
    op.drop_table('batter')
    # ### end Alembic commands ###

"""add game taable

Revision ID: 7c24fefbde0d
Revises: ff66a7bfae26
Create Date: 2020-01-18 18:29:58.174642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c24fefbde0d'
down_revision = 'ff66a7bfae26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('opponent_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['opponent_id'], ['opponent.id'], ),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_date'), 'game', ['date'], unique=False)
    op.create_index(op.f('ix_game_opponent_id'), 'game', ['opponent_id'], unique=False)
    op.create_index(op.f('ix_game_season_id'), 'game', ['season_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_game_season_id'), table_name='game')
    op.drop_index(op.f('ix_game_opponent_id'), table_name='game')
    op.drop_index(op.f('ix_game_date'), table_name='game')
    op.drop_table('game')
    # ### end Alembic commands ###

"""added videos table

Revision ID: 0370de8ec4b6
Revises: db376de83655
Create Date: 2020-02-06 15:51:57.079278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0370de8ec4b6'
down_revision = 'db376de83655'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('video',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('pitcher_id', sa.Integer(), nullable=True),
    sa.Column('batter_id', sa.Integer(), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['batter_id'], ['batter.id'], ),
    sa.ForeignKeyConstraint(['pitcher_id'], ['pitcher.id'], ),
    sa.ForeignKeyConstraint(['season_id'], ['season.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_batter_id'), 'video', ['batter_id'], unique=False)
    op.create_index(op.f('ix_video_date'), 'video', ['date'], unique=False)
    op.create_index(op.f('ix_video_pitcher_id'), 'video', ['pitcher_id'], unique=False)
    op.create_index(op.f('ix_video_season_id'), 'video', ['season_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_video_season_id'), table_name='video')
    op.drop_index(op.f('ix_video_pitcher_id'), table_name='video')
    op.drop_index(op.f('ix_video_date'), table_name='video')
    op.drop_index(op.f('ix_video_batter_id'), table_name='video')
    op.drop_table('video')
    # ### end Alembic commands ###
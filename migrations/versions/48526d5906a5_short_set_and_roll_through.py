"""short set and roll through

Revision ID: 48526d5906a5
Revises: ced51a5bb6ae
Create Date: 2020-02-13 12:56:53.905582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48526d5906a5'
down_revision = 'ced51a5bb6ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pitch', sa.Column('roll_through', sa.Boolean(), nullable=True))
    op.add_column('pitch', sa.Column('short_set', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_pitch_roll_through'), 'pitch', ['roll_through'], unique=False)
    op.create_index(op.f('ix_pitch_short_set'), 'pitch', ['short_set'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_pitch_short_set'), table_name='pitch')
    op.drop_index(op.f('ix_pitch_roll_through'), table_name='pitch')
    op.drop_column('pitch', 'short_set')
    op.drop_column('pitch', 'roll_through')
    # ### end Alembic commands ###

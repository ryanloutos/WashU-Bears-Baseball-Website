"""empty message

Revision ID: 0e460bb6bfe1
Revises: 989547dd94e6
Create Date: 2019-12-18 20:24:07.533047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e460bb6bfe1'
down_revision = '989547dd94e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_opponent_name'), 'opponent', ['name'], unique=False)
    
    with op.batch_alter_table('outing') as batch_op:
        batch_op.drop_index('ix_outing_opponent')
        batch_op.drop_column('opponent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('outing', sa.Column('opponent', sa.VARCHAR(length=32), nullable=True))
    op.create_index('ix_outing_opponent', 'outing', ['opponent'], unique=False)
    op.drop_index(op.f('ix_opponent_name'), table_name='opponent')
    # ### end Alembic commands ###

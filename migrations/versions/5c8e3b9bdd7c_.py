"""empty message

Revision ID: 5c8e3b9bdd7c
Revises: cf37f26ca26f
Create Date: 2020-03-18 12:07:17.294723

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c8e3b9bdd7c'
down_revision = 'cf37f26ca26f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('season') as batch_op:
        batch_op.add_column(sa.Column('semester', sa.String(length=8), nullable=True))
        batch_op.create_index(op.f('ix_season_semester'), ['semester'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_season_semester'), table_name='season')
    op.drop_column('season', 'semester')
    # ### end Alembic commands ###

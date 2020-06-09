"""player and coach columns

Revision ID: 72ca94739b34
Revises: 4acb88ed85ac
Create Date: 2020-06-09 13:09:10.785903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72ca94739b34'
down_revision = '4acb88ed85ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('current_coach', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('current_player', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_user_current_coach'), 'user', ['current_coach'], unique=False)
    op.create_index(op.f('ix_user_current_player'), 'user', ['current_player'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_current_player'), table_name='user')
    op.drop_index(op.f('ix_user_current_coach'), table_name='user')
    op.drop_column('user', 'current_player')
    op.drop_column('user', 'current_coach')
    # ### end Alembic commands ###

"""empty message

Revision ID: 15a2dffaf196
Revises: 2e90bd59c7ae
Create Date: 2020-12-30 17:49:02.570259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15a2dffaf196'
down_revision = '2e90bd59c7ae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resource') as batch_op:
        batch_op.drop_column('article_link')
        batch_op.drop_column('video_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('resource', sa.Column(
        'video_link', sa.VARCHAR(length=256), nullable=True))
    op.add_column('resource', sa.Column('article_link',
                                        sa.VARCHAR(length=256), nullable=True))
    op.drop_index(op.f('ix_opponent_mascot'), table_name='opponent')
    # ### end Alembic commands ###

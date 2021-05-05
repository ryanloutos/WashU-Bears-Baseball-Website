"""empty message

Revision ID: a7275705df1d
Revises: 15a2dffaf196
Create Date: 2020-12-30 20:40:55.528220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7275705df1d'
down_revision = '15a2dffaf196'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resource') as batch_op:
        batch_op.alter_column('category',
                              existing_type=sa.VARCHAR(length=32),
                              nullable=False)
        batch_op.alter_column('resource_type',
                              existing_type=sa.VARCHAR(length=32),
                              nullable=False)
        batch_op.alter_column('title',
                              existing_type=sa.VARCHAR(length=32),
                              nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('resource', 'title',
                    existing_type=sa.VARCHAR(length=32),
                    nullable=True)
    op.alter_column('resource', 'resource_type',
                    existing_type=sa.VARCHAR(length=32),
                    nullable=True)
    op.alter_column('resource', 'category',
                    existing_type=sa.VARCHAR(length=32),
                    nullable=True)
    op.drop_index(op.f('ix_opponent_mascot'), table_name='opponent')
    # ### end Alembic commands ###
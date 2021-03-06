"""add atbat_id to video table

Revision ID: 549f9aa3addb
Revises: ae33a696e946
Create Date: 2020-02-28 10:59:43.534566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '549f9aa3addb'
down_revision = 'ae33a696e946'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('video') as batch_op:
        batch_op.add_column(sa.Column('atbat_id', sa.Integer(), nullable=True))
        batch_op.create_index(op.f('ix_video_atbat_id'), ['atbat_id'], unique=False)
        batch_op.create_foreign_key("None", 'at_bat', ['atbat_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'video', type_='foreignkey')
    op.drop_index(op.f('ix_video_atbat_id'), table_name='video')
    op.drop_column('video', 'atbat_id')
    # ### end Alembic commands ###

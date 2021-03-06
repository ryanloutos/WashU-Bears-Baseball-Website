"""empty message

Revision ID: 989547dd94e6
Revises: e4502b2cd507
Create Date: 2019-12-18 12:22:30.160328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '989547dd94e6'
down_revision = 'e4502b2cd507'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('outing') as batch_op: 
        batch_op.create_foreign_key('None', 'season', ['season_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'outing', type_='foreignkey')
    # ### end Alembic commands ###

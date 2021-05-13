"""empty message

Revision ID: 650c5800cdef
Revises: d4bd87c0ddf0
Create Date: 2021-05-12 00:42:22.562790

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '650c5800cdef'
down_revision = 'd4bd87c0ddf0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'mail')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('mail', sa.VARCHAR(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###

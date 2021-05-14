"""Order status enum

Revision ID: 91e16cffa5ac
Revises: 55e5a4aa1070
Create Date: 2021-05-12 18:05:06.970135

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils import ChoiceType
from app import OrderStatusType

# revision identifiers, used by Alembic.
revision = '91e16cffa5ac'
down_revision = '55e5a4aa1070'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('orders', 'status')
    op.add_column('orders', sa.Column('status', ChoiceType(OrderStatusType), default='New'))


def downgrade():
    op.drop_column('orders', 'status')
    op.add_column('orders', sa.Column('status', sa.String(), nullable=False), )

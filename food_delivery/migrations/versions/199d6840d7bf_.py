"""empty message

Revision ID: 199d6840d7bf
Revises: 91e16cffa5ac
Create Date: 2021-05-12 21:33:51.761668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '199d6840d7bf'
down_revision = '91e16cffa5ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'status',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, default=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_admin')
    op.alter_column('orders', 'status',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    # ### end Alembic commands ###
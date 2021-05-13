"""empty message

Revision ID: 55e5a4aa1070
Revises: 650c5800cdef
Create Date: 2021-05-12 01:26:43.092607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55e5a4aa1070'
down_revision = '650c5800cdef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(), nullable=False))
    op.add_column('users', sa.Column('name', sa.String(length=50), nullable=False))
    op.drop_constraint('users_mail_key', 'users', type_='unique')
    op.create_unique_constraint(None, 'users', ['email'])
    op.drop_column('users', 'mail')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('mail', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'users', type_='unique')
    op.create_unique_constraint('users_mail_key', 'users', ['mail'])
    op.drop_column('users', 'name')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###

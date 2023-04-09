"""empty message

Revision ID: e5eba289550b
Revises: 4fe71ac14b01
Create Date: 2023-04-09 13:30:20.783585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5eba289550b'
down_revision = '4fe71ac14b01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channel', sa.Column('channelNSFW', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('channel', 'channelNSFW')
    # ### end Alembic commands ###

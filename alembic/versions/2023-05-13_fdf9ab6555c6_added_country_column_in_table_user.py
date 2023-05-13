"""added country column in table user

Revision ID: fdf9ab6555c6
Revises: 316710db929a
Create Date: 2023-05-13 20:28:30.275732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdf9ab6555c6'
down_revision = '316710db929a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('country', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'country')
    # ### end Alembic commands ###

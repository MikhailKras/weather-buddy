"""update table user with latitude and longitude

Revision ID: b47c89ad635c
Revises: fdf9ab6555c6
Create Date: 2023-05-15 21:36:29.520447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b47c89ad635c'
down_revision = 'fdf9ab6555c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('longitude', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'longitude')
    op.drop_column('user', 'latitude')
    # ### end Alembic commands ###

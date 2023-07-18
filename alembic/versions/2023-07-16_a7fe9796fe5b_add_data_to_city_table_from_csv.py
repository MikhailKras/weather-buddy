"""add data to city table from csv

Revision ID: a7fe9796fe5b
Revises: bda0f8f7aba4
Create Date: 2023-07-16 19:07:14.612094

"""
import csv
import os

from alembic import op
from sqlalchemy import Table

from src.database import metadata

# revision identifiers, used by Alembic.
revision = 'a7fe9796fe5b'
down_revision = 'bda0f8f7aba4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    migration_script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_file_path = os.path.join(migration_script_dir, '..', '..', 'city_data', 'city.csv')

    with open(csv_file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        rows = list(csv_reader)

    table = Table('city', metadata, autoload=True)

    processed_rows = []
    for row in rows:
        processed_row = {
            'id': int(row['id']),
            'name': row['name'],
            'region': row['region'],
            'country': row['country'],
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'population': int(row['population']),
            'timezone': row['timezone'],
            'alternatenames': [item.strip() for item in row['alternatenames'][1:-1].split(',')]
        }
        processed_rows.append(processed_row)

    op.bulk_insert(table, processed_rows)
    # ### end Alembic commands ###


def downgrade() -> None:
    table = Table('city', metadata, autoload=True)
    op.execute(table.delete())
    # ### end Alembic commands ###

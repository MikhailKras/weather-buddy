from sqlalchemy import Table, Column, Integer, String, Float, CheckConstraint, ARRAY

from src.database import metadata

city = Table(
    'city',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('region', String),
    Column('country', String, nullable=False),
    Column('latitude', Float, CheckConstraint('latitude >= -90.0 AND latitude <= 90.0')),
    Column('longitude', Float, CheckConstraint('longitude >= -180.0 AND longitude <= 180.0')),
    Column('population', Integer),
    Column('timezone', String),
    Column('alternatenames', ARRAY(String))
)

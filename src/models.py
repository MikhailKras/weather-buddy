from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Float, CheckConstraint, ARRAY, ForeignKey, TIMESTAMP
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
search_history_city_name_db = Table(
    'search_history_city_name',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('city_id', Integer, ForeignKey('city.id'), nullable=False),
    Column('request_at', TIMESTAMP, default=datetime.utcnow),
)


search_history_coordinates_db = Table(
    'search_history_coordinates',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('latitude', Float),
    Column('longitude', Float),
    Column('place_name', String),
    Column('region', String),
    Column('country', String),
    Column('request_at', TIMESTAMP, default=datetime.utcnow),
)

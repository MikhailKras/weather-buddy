from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP, Float, CheckConstraint

metadata = MetaData()

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('email', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('city', String, nullable=False),
    Column('country', String, nullable=False, default='No data'),
    Column('disabled', Boolean, nullable=False, default=False),
    Column('registered_at', TIMESTAMP, default=datetime.utcnow),
    Column('latitude', Float, CheckConstraint('latitude >= -90.0 AND latitude <= 90.0')),
    Column('longitude', Float, CheckConstraint('longitude >= -180.0 AND longitude <= 180.0'))
)

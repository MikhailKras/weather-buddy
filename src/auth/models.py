from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP, Float, CheckConstraint, ForeignKey

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

email_verification = Table(
    'email_verification',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('token', String, nullable=False),
    Column('verified', Boolean, nullable=False, default=False),
    Column('created_at', TIMESTAMP, default=datetime.utcnow)
)

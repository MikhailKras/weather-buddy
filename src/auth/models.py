from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Boolean, TIMESTAMP, ForeignKey

from src.database import metadata

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('email', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('city_id', Integer, ForeignKey('city.id'), nullable=False),
    Column('disabled', Boolean, nullable=False, default=False),
    Column('registered_at', TIMESTAMP, default=datetime.utcnow),
)

email_verification = Table(
    'email_verification',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('token', String, nullable=False),
    Column('verified', Boolean, nullable=False, default=False),
)

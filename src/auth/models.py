from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP

metadata = MetaData()

user = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('email', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('city', String, nullable=False),
    Column('disabled', Boolean, nullable=False, default=False),
    Column('registered_at', TIMESTAMP, default=datetime.utcnow),
)

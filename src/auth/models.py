from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP

from src.database import Base

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


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    city = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)

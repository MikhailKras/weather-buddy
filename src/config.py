import os

from dotenv import load_dotenv

load_dotenv(override=False)

CLIENT_ORIGIN = os.getenv('CLIENT_ORIGIN')

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

DB_HOST_TEST = os.getenv("DB_HOST_TEST")
DB_PORT_TEST = os.getenv("DB_PORT_TEST")
DB_NAME_TEST = os.getenv("DB_NAME_TEST")
DB_USER_TEST = os.getenv("DB_USER_TEST")
DB_PASS_TEST = os.getenv("DB_PASS_TEST")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

RATE_LIMITER_FLAG = os.environ.get("RATE_LIMITER_FLAG")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

SECRET_KEY_REG = os.getenv('SECRET_KEY_REG')

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
SECRET_KEY_EMAIL_VERIFICATION = os.getenv('SECRET_KEY_EMAIL_VERIFICATION')

SECRET_KEY_RESET_PASSWORD = os.getenv('SECRET_KEY_RESET_PASSWORD')

MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_NAME = os.getenv('MONGODB_NAME')
MONGODB_URL = os.getenv('MONGODB_URL')
MONGODB_COLLECTION_NAME = os.getenv('MONGODB_COLLECTION_NAME')

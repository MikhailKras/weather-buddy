from celery import Celery

from src.config import REDIS_HOST, REDIS_PORT

celery = Celery("src", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}", include=['src.auth.tasks'])

celery.conf.broker_connection_retry_on_startup = True

if __name__ == '__main__':
    celery.start()

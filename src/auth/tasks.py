from src.celery_app import celery
from src.auth.email import Email


@celery.task
def task_send_reset_password_mail(username, url, email):
    Email(username, url, email).send_reset_password_mail()


@celery.task
def task_send_verification_code(username, url, email):
    Email(username, url, email).send_verification_code()
    
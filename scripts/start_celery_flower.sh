#!/bin/bash

celery -A src.celery_app:celery worker &

sleep 2

celery -A src.celery_app:celery flower

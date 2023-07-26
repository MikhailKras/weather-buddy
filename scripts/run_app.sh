#!/bin/bash

redis-server &

sleep 1

uvicorn src.main:app --reload --host 0.0.0.0 --port 1234 &

sleep 1

celery -A src.celery_app:celery worker &

sleep 2

celery -A src.celery_app:celery flower

FROM python:3.11

WORKDIR /fastapi-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod 777 scripts/*.sh

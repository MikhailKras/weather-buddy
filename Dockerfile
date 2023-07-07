FROM python:3.11

WORKDIR /fastapi-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod 777 scripts/*.sh

CMD [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1235" ]

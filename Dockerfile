FROM python:3.10-alpine

ENV MODULE_NAME=app.app
ENV STAGE=DEV
ENV PYTHONPATH="./app"

COPY ./app/requirements.txt /
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /app
WORKDIR /app

CMD ["gunicorn", "-w 4", "--bind", "127.0.0.1:8081", "app:app"]
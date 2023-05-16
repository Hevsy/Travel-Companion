FROM tiangolo/meinheld-gunicorn:python3.9

ENV MODULE_NAME=app.app
ENV STAGE=DEV

COPY ./app /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
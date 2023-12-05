FROM python:3.10-slim

WORKDIR /code


COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r app/requirements.txt

COPY ./app ./app
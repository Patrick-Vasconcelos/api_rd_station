FROM python:3.10-slim

WORKDIR /app


COPY requirements.txt .
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# CMD ["python", "main.py"]
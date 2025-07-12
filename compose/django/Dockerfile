FROM python:3.13.5-slim

WORKDIR /app


RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt --no-cache-dir


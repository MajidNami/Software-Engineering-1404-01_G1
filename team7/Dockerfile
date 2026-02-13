# Team 7 Dockerfile
# Note: This Dockerfile is NOT used in the standard deployment.
# The main project Dockerfile (in root) handles all team services.
# This file is kept for reference or standalone team7 development only.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Install main project requirements first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install team7 specific requirements
COPY team7/requirements.txt /app/team7/
RUN pip install --no-cache-dir -r team7/requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["bash","-lc","python manage.py migrate team7 --database=team7 && python manage.py seed_questions && gunicorn app404.wsgi:application -b 0.0.0.0:8000"]


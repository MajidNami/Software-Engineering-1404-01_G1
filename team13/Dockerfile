FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Only Django dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/team13/
COPY templates/team13/ /app/templates/team13/
COPY static/team13/ /app/static/team13/

EXPOSE 8000
CMD ["bash", "-c", "cd /app && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn app404.wsgi:application -b 0.0.0.0:8000"]

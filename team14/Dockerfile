FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 👇 الان هم app404 و هم team14 کپی می‌شن
COPY . .

EXPOSE 8000

CMD ["gunicorn", "app404.wsgi:application", "-b", "0.0.0.0:8000"]

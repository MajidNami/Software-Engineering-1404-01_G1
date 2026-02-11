FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir Django==4.2.27 PyJWT django-environ django-cors-headers PyMySQL gunicorn whitenoise openai djangorestframework django-filter dj-database-url

COPY . /app/

EXPOSE 8000

CMD ["bash", "-lc", "python manage.py migrate --database=team15 && python manage.py load_mock_data && python manage.py collectstatic --noinput && gunicorn app404.wsgi:application -b 0.0.0.0:8000"]

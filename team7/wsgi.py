import os
from django.core.wsgi import get_wsgi_application

# Revert to standard Django path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team7.settings')

application = get_wsgi_application()

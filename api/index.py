from wordastra.wsgi import application
from django.core.wsgi import get_wsgi_application
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordastra.settings')
django.setup()

def handler(request, response):
    return application(request.environ, response.start_response)
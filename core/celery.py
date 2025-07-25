import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')

app = Celery('realestate')
app.conf.enable_utc = False
app.conf.update(timezone='Africa/Nairobi')

# Using a string here means the worker doesn't have to serialize
# the configuration object.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
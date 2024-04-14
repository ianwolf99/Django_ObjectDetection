from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'object_detection.settings')

app = Celery('object_detection')

# Using the Django settings module to configure the Celery app
app.config_from_object(settings, namespace='CELERY')

# Auto-discover tasks in all registered Django app configs.
app.autodiscover_tasks()

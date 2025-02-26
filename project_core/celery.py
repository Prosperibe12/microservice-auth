from __future__ import absolute_import, unicode_literals
import os 
from decouple import config
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_core.settings')

app = Celery('project_core', broker=config('CLOUD_AMQP_URL'))
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
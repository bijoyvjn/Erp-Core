import os
from celery import Celery

# 1. Point to Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. Create Celery instance
app = Celery('core')

# 3. Read config from settings.py using CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# 4. Auto-discover tasks.py across all apps
app.autodiscover_tasks()
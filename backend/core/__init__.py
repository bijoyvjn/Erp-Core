from .celery import app as celery_app

# Expose 'app' so Celery can find it automatically
app = celery_app

__all__ = ('celery_app', 'app')
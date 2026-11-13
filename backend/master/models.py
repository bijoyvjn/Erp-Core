from django.db import models
import uuid
from django.conf import settings

class BaseModel(models.Model):
    uniqueid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_updated")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True
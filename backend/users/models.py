from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        return str(self.username)
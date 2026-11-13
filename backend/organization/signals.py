from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import *


@receiver([post_save, post_delete], sender=Department)
def invalidate_department_cache(sender, instance, **kwargs):
    cache.delete_pattern("department_list_*")

@receiver([post_save, post_delete], sender=Employee)
def invalidate_employee_cache(sender, instance, **kwargs):
    cache.delete_pattern("employee_list_*")

@receiver([post_save, post_delete], sender=Project)
def invalidate_project_cache(sender, instance, **kwargs):
    cache.delete_pattern("projects_list_*")

@receiver([post_save, post_delete], sender=ProjectAllocation)
def invalidate_project_allocation_cache(sender, instance, **kwargs):
    cache.delete_pattern("project_allocation_list_*")

from rest_framework.permissions import BasePermission
from organization.models import *


class IsHR(BasePermission):
    message = "Only HR users can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        hr_check = Employee.objects.filter(user=request.user,designation="HR").exists()
        return hr_check


class IsSuperUser(BasePermission):
    message = "Only superuser can perform this action."

    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_superuser)


class IsHROrSuperUser(BasePermission):
    message = "Only HR or Superuser users can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        is_hr = Employee.objects.filter(user=request.user,designation="HR").exists()
        is_superuser = request.user.is_superuser
        return is_hr or is_superuser
from django.db import models
from django.conf import settings
from master.models import *

class Department(BaseModel):
    name = models.CharField(max_length=150, unique=True, db_index=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Employee(BaseModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    designation = models.CharField(max_length=150, db_index=True)
    joining_date = models.DateField(db_index=True)
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PROBATION = 'PROBATION', 'Probation'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        TERMINATED = 'TERMINATED', 'Terminated'
        RESIGNED = 'RESIGNED', 'Resigned'
    employment_status = models.CharField(max_length=20, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE, db_index=True)
    location = models.CharField(max_length=100, db_index=True)

    class Meta:
        db_table = 'employees'
        ordering = ['-joining_date']
        indexes = [
            models.Index(fields=['department', 'employment_status']),
            models.Index(fields=['manager', 'employment_status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.user.get_full_name()}"


class Project(BaseModel):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED, db_index=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM, db_index=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectAllocation(BaseModel):
    class Status(models.TextChoices):
        YET_TO_START = 'YET_TO_START', 'Yet To Start'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        ON_HOLD = 'ON_HOLD', 'On Hold'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='Pro_allocation')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='pro_allocation_employee')
    assigned_date = models.DateField(auto_now_add=True)
    completed_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.YET_TO_START, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'project_allocations'

    def __str__(self):
        return f"{self.project.code} - {self.employee.code}"
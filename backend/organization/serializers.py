from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(source='employees.count', read_only=True)

    class Meta:
        model = Department
        fields = ['uniqueid','name', 'code', 'description', 'is_active', 'employee_count']
        read_only_fields = ['uniqueid']


class EmployeeListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.user.get_full_name', read_only=True)

    class Meta:
        model = Employee
        fields = ['uniqueid', 'code', 'user_email', 'full_name', 'department', 'department_name', 'designation', 'employment_status', 
            'joining_date', 'location', 'manager', 'manager_name']
        read_only_fields = ['uniqueid']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['code', 'user', 'department', 'manager', 'designation', 'joining_date', 'employment_status', 'location']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['code', 'user', 'department', 'manager', 'designation', 'joining_date', 'employment_status', 'location']

    def validate_code(self, value):
        instance = getattr(self, 'instance', None)
        if Employee.objects.filter(code=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("An employee with this code already exists.")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['uniqueid', 'code', 'name', 'description', 'budget', 'start_date', 'end_date', 'status', 'priority']
        read_only_fields = ['uniqueid']


class ProjectAllocationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAllocation
        fields = ['uniqueid', 'project', 'employee', 'assigned_date', 'completed_date', 'status', 'is_active']
        read_only_fields = ['uniqueid']


class ProjectAllocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAllocation
        fields = ['project', 'employee', 'assigned_date', 'completed_date', 'status', 'is_active']


class ProjectAllocationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAllocation
        fields = ['uniqueid', 'project', 'employee', 'assigned_date', 'completed_date', 'status', 'is_active']
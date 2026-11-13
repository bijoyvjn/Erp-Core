from django.urls import path
from .views import *

urlpatterns = [
    path('departments/', DepartmentListCreateAPIView.as_view(), name='department-list-create'),
    path('departments/<uuid:pk>/', DepartmentDetailAPIView.as_view(), name='department-detail'),

    path('employees/', EmployeeListCreateAPIView.as_view(), name='employee-list-create'),
    path('employees/<uuid:pk>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),

    path('projects/', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('projects/<uuid:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),

    path('project-allocation/', ProjectAllocationListCreateAPIView.as_view(), name='project-allocation-list-create'),
    path('project-allocation/<uuid:pk>/', ProjectAllocationDetailAPIView.as_view(), name='project-allocation-detail'),
]
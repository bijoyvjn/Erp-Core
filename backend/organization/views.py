from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q
import uuid
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *
from permissions import *
from .tasks import send_allocation_email
from .services import notify_events_microservice

import logging
# logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# DEPARTMENT API VIEWS

class DepartmentListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method=="POST":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    pagination_class = StandardResultsSetPagination
    serializer_class = DepartmentSerializer

    def get(self, request):
        query_params = request.GET.urlencode()
        cache_key = f"department_list_{query_params}" if query_params else "department_list_page_1"
        
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)
    
        queryset = Department.objects.all()
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)

        cache.set(cache_key, paginated_response.data, timeout=60 * 15)
        return paginated_response
    

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method!="GET":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        return get_object_or_404(Department, pk=pk)

    def get(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department)
        return Response({"success": True, "data": serializer.data})

    def put(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        department = self.get_object(pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        department = self.get_object(pk)
        if department.employees.exists():
            return Response({"success": False, "error": "Cannot delete department assigned to existing employees."},status=status.HTTP_400_BAD_REQUEST)
        department.delete()
        return Response({"success": True, "message": "Department deleted successfully."},status=status.HTTP_204_NO_CONTENT)

# EMPLOYEE API VIEWS

class EmployeeListCreateAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    pagination_class = StandardResultsSetPagination
    serializer_class = EmployeeListSerializer
    
    def get(self,request):
        query_params = request.GET.urlencode()
        cache_key = f"employee_list_{query_params}" if query_params else "employee_list_page_1"
        
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)
        
        queryset = Employee.objects.select_related('user','department','manager').all()
        paginator = self.pagination_class()
        paginated_query = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_query, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)

        cache.set(cache_key, paginated_response.data, timeout=60 * 15)
        return paginated_response

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    pagination_class = StandardResultsSetPagination
    serializer_class = EmployeeDetailSerializer

    def get_object(self, pk):
        return get_object_or_404(Employee, pk=pk)

    def get(self, request, pk):
        employee = self.get_object(pk)
        serializer = self.serializer_class(employee)
        return Response({"success": True, "data": serializer.data})

    def put(self, request, pk):
        employee = self.get_object(pk)
        serializer = self.serializer_class(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        employee = self.get_object(pk)
        serializer = self.serializer_class(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        employee = self.get_object(pk)
        employee.delete()
        return Response({"success": True, "message": "Employee deleted successfully."},status=status.HTTP_204_NO_CONTENT)

# PROJECT API VIEWS

class ProjectListCreateAPIView(APIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = ProjectListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    def get(self,request):
        query_params = request.GET.urlencode()
        cache_key = f"projects_list_{query_params}" if query_params else "projects_list_page_1"
        
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)
        
        queryset = Project.objects.all()
        paginator = self.pagination_class()
        paginated_query = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_query, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)

        cache.set(cache_key, paginated_response.data, timeout=60 * 15)
        return paginated_response

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    pagination_class = StandardResultsSetPagination
    serializer_class = ProjectListSerializer

    def get_object(self, pk):
        return get_object_or_404(Project, pk=pk)

    def get(self, request, pk):
        project = self.get_object(pk)
        serializer = self.serializer_class(project)
        return Response({"success": True, "data": serializer.data})

    def put(self, request, pk):
        project = self.get_object(pk)
        serializer = self.serializer_class(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        project = self.get_object(pk)
        serializer = self.serializer_class(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = self.get_object(pk)
        project.delete()
        return Response({"success": True, "message": "Project deleted successfully."},status=status.HTTP_204_NO_CONTENT)

         

# PROJECT ALLOCATION API VIEWS

class ProjectAllocationListCreateAPIView(APIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = ProjectAllocationListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    def get(self,request):
        query_params = request.GET.urlencode()
        cache_key = f"project_allocation_list_{query_params}" if query_params else "project_allocation_list_page_1"
        cached_response = cache.get(cache_key)

        if cached_response is not None:
            return Response(cached_response)
        
        queryset = ProjectAllocation.objects.select_related('project','employee').all()
        paginator = self.pagination_class()
        paginated_query = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_query, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        cache.set(cache_key, paginated_response.data, timeout=60 * 15)
        return paginated_response

    def post(self, request):
        serializer = ProjectAllocationCreateSerializer(data=request.data)
        if serializer.is_valid():
            allocation = serializer.save()

            # celery email sender
            transaction.on_commit(lambda: send_allocation_email.delay(allocation.employee.code,allocation.project.code))
            # Microservice Notification
            transaction.on_commit(lambda: notify_events_microservice(allocation))

            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectAllocationDetailAPIView(APIView):

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsHROrSuperUser()]
        return [IsAuthenticated()]

    pagination_class = StandardResultsSetPagination
    serializer_class = ProjectAllocationDetailsSerializer

    def get_object(self, pk):
        return get_object_or_404(ProjectAllocation, pk=pk)

    def get(self, request, pk):
        allocation = self.get_object(pk)
        serializer = self.serializer_class(allocation)
        return Response({"success": True, "data": serializer.data})

    def put(self, request, pk):
        allocation = self.get_object(pk)
        serializer = self.serializer_class(allocation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        allocation = self.get_object(pk)
        serializer = self.serializer_class(allocation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        allocation = self.get_object(pk)
        allocation.delete()
        return Response({"success": True, "message": "Project Allocation deleted successfully."},status=status.HTTP_200_OK)


    






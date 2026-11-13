from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # JWT
    path("api/auth/login/", TokenObtainPairView.as_view(),name="token_obtain_pair",),
    path("api/auth/refresh/",TokenRefreshView.as_view(),name="token_refresh",),
    # Apps
    path('users/', include('users.urls')),
    path('org/', include('organization.urls')),
]


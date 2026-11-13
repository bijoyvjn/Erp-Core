from django.urls import path
from .views import *


urlpatterns = [
    path('userslist/', UserListApiView.as_view(), name='user-list-create'),
]
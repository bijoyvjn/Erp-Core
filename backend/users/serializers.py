from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class UserListSerializer(serializers.ModelSerializer):
    # user_email = serializers.EmailField(source='user.email', read_only=True)
    # full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','email', 'first_name', 'phone']
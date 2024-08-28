from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password_hash', 'user_name', 'nick_name', 'phone_number', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super(UserSerializer, self).create(validated_data)
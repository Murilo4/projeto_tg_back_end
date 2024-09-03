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
    
    def validate_nick_name(self, value):
        if User.objects.filter(nick_name=value).exists():
            raise serializers.ValidationError("This username is not available. Try a suggested username or enter a new one.")
        return value

    def validate_password_hash(self, value):
        if value != self.initial_data.get('confirm_password'):
            raise serializers.ValidationError("Passwords must match.")
        return value
    
    def create(self, validated_data):
        # Hash a senha antes de salvar
        validated_data['password_hash'] = make_password(validated_data['password_hash'])
        
        # Cria e retorna o usuário
        user = User(**validated_data)  # Cria um novo objeto User
        user.save()  # Salva no banco de dados
        return user
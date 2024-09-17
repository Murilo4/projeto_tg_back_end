from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'user_name', 'nick_name', 'phone_number', 'created_at', 'updated_at')

    def validate_user_name(self, value):
        errors = {}

        if User.objects.filter(user_name=value).exists():
            errors["username_exists"] = "USERNAME_EXISTS"
        # Verificar o tamanho do nome de usuário
        if len(value) < 2:
            errors["username_too_short"] = "USERNAME_TOO_SHORT"

        if len(value) > 50:
            errors["username_too_big"] = "USERNAME_TOO_BIG"

        if errors:
            raise serializers.ValidationError(errors)
        
        return value
    
    def validate_email(self, value):
        errors = {}

        if User.objects.filter(email=value).exists():
            errors["email_exists"] = "EMAIL_EXISTS"

        if errors:
            raise serializers.ValidationError(errors)
        
        return value
    
    def create(self, validated_data):
        # Hash a senha antes de salvar
        
        # Cria e retorna o usuário
        user = User(**validated_data)  # Cria um novo objeto User
        user.save()  # Salva no banco de dados
        return user
    

class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('user_name')
        password = data.get('password_hash')
        

        try:
            user = User.objects.get(user_name=username)
        
            if not User.check_password(self, password):
                print('ih rapaiz')  # Verifica a senha com o método do modelo
                raise ValidationError('Invalid credentials')
        except User.DoesNotExist:
            raise ValidationError('Invalid credentials')

        data['user'] = user  # Adiciona o usuário autenticado aos atributos
        return data
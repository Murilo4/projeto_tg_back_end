from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'user_name', 'nick_name', 'created_at', 'updated_at')

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
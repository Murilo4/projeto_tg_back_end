from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password_hash', 'user_name', 'nick_name', 'phone_number', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['password_hash'] = make_password(validated_data['password_hash'])
        return super(UserSerializer, self).create(validated_data)
    
    def validate_user_name(self, value):
        if User.objects.filter(user_name=value).exists():
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
    

class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('user_name')
        password = data.get('password_hash')
        

        print(password)
        try:
            user = User.objects.get(user_name=username)
        
            if not User.check_password(self, password):
                print('ih rapaiz')  # Verifica a senha com o método do modelo
                raise ValidationError('Invalid credentials')
        except User.DoesNotExist:
            raise ValidationError('Invalid credentials')

        data['user'] = user  # Adiciona o usuário autenticado aos atributos
        return data
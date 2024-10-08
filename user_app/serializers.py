from rest_framework import serializers
from .models import User, TempRegistration


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'user_name', 'nick_name')

    def create(self, validated_data):
        # Cria e retorna o usuário
        user = User(**validated_data)  # Cria um novo objeto User
        user.save()  # Salva no banco de dados
        return user


class UserChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'user_name', 'nick_name', 'phone_number',
                  'user_img')

        def update(self, validated_data):
            user = User(**validated_data)
            user.save()
            return user


class TempUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempRegistration
        fields = ('email', 'user_name', 'nick_name')

    def create(self,  validated_data):
        temp_user = TempRegistration(**validated_data)
        temp_user.save()
        return temp_user

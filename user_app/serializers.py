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

        def update(self, instance, validated_data):
            instance.email = validated_data.get(
                'email', instance.email)
            instance.user_name = validated_data.get(
                'user_name', instance.user_name)
            instance.nick_name = validated_data.get(
                'nick_name', instance.nick_name)
            instance.phone_number = validated_data.get(
                'phone_number', instance.phone_number)
            instance.user_img = validated_data.get(
                'user_img', instance.user_img)

            # Salva a instância do usuário no banco de dados
            instance.save()

            return instance


class TempUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempRegistration
        fields = ('email', 'user_name', 'nick_name')

    def create(self,  validated_data):
        temp_user = TempRegistration(**validated_data)
        temp_user.save()
        return temp_user
    

class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'user_name', 'nick_name', 'phone_number',
                  'user_img')

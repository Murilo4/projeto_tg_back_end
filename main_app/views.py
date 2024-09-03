from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

# Create your views here.

@api_view(['GET'])
def get_user(request):
    if request.method == 'GET':
        users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_by_nick(request, id):
    try:
        user = User.objects.get(pk=id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)



@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
            try:
                new_user = request.data
                serializer = UserSerializer(data=new_user)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                print(f'{e.detail}')
                return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('user_name')
    password = request.data.get('password_hash')

    user = User.objects.get(user_name=username)
    if user.create(password):
            # Gera ou recupera o token do usuário
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@login_required(login_url="login/")
@api_view(['GET', 'PUT', 'DELETE'])
def user_manager(request):
    if request.method == 'GET':
        try:
            if request.GET['user']:
                user_id = request.GET['user']

                try:
                    user = User.objects.get(pk=user_id)
                except ValidationError as e:
                    print(f'{e.detail}')
                    return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                print(f'{e.detail}')
                return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

    elif request.method == 'PUT':
        user_id = request.GET.get('user')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except ValidationError as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
        
    
        

    
    
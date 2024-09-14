from django.shortcuts import render
import random
import string
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, LoginSerializer
from .models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.cache import cache
from django.views import View

def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

LOGIN_REDIRECT_URL = '/login'


@api_view(['GET', 'PUT', 'DELETE'])
def user_manager(request, id):  # Aqui você deve receber o parâmetro id
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=id)  # Usa o id recebido na URL
            serializer = UserSerializer(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    elif request.method == 'DELETE':
        try:
            user = User.objects.get(pk=id)
            user = request.user
            if user.is_authenticated:
                user.delete()
                return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            JsonResponse({'error': 'User not avaible'})
            
        
# Create your views here.
@api_view(['GET'])
def get_home(request):
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_by_nick(request, id):
    try:
        user = User.objects.get(pk=id)
    except:
        return JsonResponse(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)



@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
            try:
                new_user = request.data
                serializer = UserSerializer(data=new_user)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    user = serializer.save()
                    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                print(f'{e.detail}')
                return JsonResponse({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)

def confirmation_code(request):
    if request.method == 'POST':
        email = request.data.get('email')
        try:
            print("Enviado o email")
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        confirmation_code = generate_confirmation_code()
        cache.set(f'confirmation_code_{email}', confirmation_code, timeout=300)  # Armazenar no cache por 5 minutos

        # Salvar o código de confirmação no usuário (opcional)
        user.confirmation_code = confirmation_code
        user.save()

        # Enviar e-mail de confirmação
        try:
            send_mail(
                'Confirmação de Cadastro',
                f'Seu código de confirmação é: {confirmation_code}',
                'seuemail@dominio.com',
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({"message": "Confirmation code sent."}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)

class VerifyConfirmationCodeView(View):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('confirmation_code')

        # Verificar o código no cache
        cached_code = cache.get(f'confirmation_code_{email}')

        if cached_code and cached_code == code:
            # Código correto, marque o e-mail como verificado
            user = User.objects.get(email=email)
            user.is_email_verified = True  # Se você tiver esse campo no seu modelo
            user.save()
            return JsonResponse({"message": "Email verified successfully."}, status=200)
        else:
            return JsonResponse({"error": "Invalid or expired confirmation code."}, status=400)

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']  # Obtém a instância do usuário autenticado
        token, created = Token.objects.get_or_create(user=user)  # Cria ou obtém o token do usuário
        
        return JsonResponse({
            'token': token.key,        # Retorna o token
            'user_id': user.id         # Retorna o ID do usuário autenticado
        }, status=status.HTTP_200_OK)
    
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
        

    
    
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
from django.core.cache import cache
from django.views import View
from mailersend import emails
from dotenv import load_dotenv
import os

from django.views.decorators.csrf import csrf_exempt
load_dotenv()


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
            
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request):
    confirmation_code = generate_confirmation_code()
    email = request.data.get('to_email')
    user_name = request.data.get('user_name', 'Recipient')
    
    # Predefinido o corpo do email
    subject = "Bem-vindo ao flashVibe!"
    html_content = f"""
        <h1>Olá, {user_name}!</h1>
        <p>Bem-vindo ao nosso serviço. Estamos felizes em tê-lo conosco.</p>
        <p>O código de segurança de 6 digitos para confirmação:</p>
        <p>{confirmation_code}</p>
        <p>Se você tiver alguma dúvida, sinta-se à vontade para entrar em contato conosco.</p>
        <p>Atenciosamente,<br>FlashVibe</p>
    """
    plaintext_content = f"Olá, {user_name}!\nBem-vindo ao nosso serviço. Estamos felizes em tê-lo conosco."

   

    mail_body = {}

    mail_from = {
        "name": "Flash Vibe",
        "email": "MS_U7xQX5@trial-3yxj6lj7ex5ldo2r.mlsender.net",
    }

    recipients = [
        {
            "name": user_name,
            "email": email,
        }
    ]
    mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))
    # Configurando os parâmetros do email
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject(subject, mail_body)
    mailer.set_html_content(html_content, mail_body)
    mailer.set_plaintext_content(plaintext_content, mail_body)

    # Enviar email
    response = mailer.send(mail_body)
    
    return Response(response, status=status.HTTP_200_OK)

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



    
        

    
    
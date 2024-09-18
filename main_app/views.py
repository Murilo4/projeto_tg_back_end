from rest_framework import status
from .models import User
from rest_framework.response import Response
from .serializers import UserSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.exceptions import ValidationError
from .code_generator import generate_confirmation_code
from django.core.cache import cache
from mailersend import emails
from dotenv import load_dotenv
import os
from firebase_admin import auth
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated

load_dotenv()

# ------------------ View para criação de usuario ---------------------
@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        new_user = request.data
        serializer = UserSerializer(data=new_user)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
    
            
# ------------------ View para envio de código de confirmação de email ---------------------      
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request):
    confirmation_code = generate_confirmation_code()
    email = request.data.get('email')
    cached_code = confirmation_code
    verification_data = {
        'code': cached_code,
        'email': email
    }
      # Verificar se o e-mail já existe no banco de dados
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email já está em uso."}, status=status.HTTP_400_BAD_REQUEST)
    
    name = request.data.get('name', 'Recipient')
    cache.set(f'confirmation_code_{email}', verification_data,  timeout=300)  # Exemplo de timeout de 5 minutos

    # Predefinido o corpo do email
    subject = "Bem-vindo ao flashVibe!"
    html_content = f"""
        <h1>Olá, {name}!</h1>
        <p>Bem-vindo ao nosso serviço.</p>
        <p>Estamos felizes em tê-lo conosco.</p>
        <p>O código de segurança de 6 digitos para confirmação do endereço de email:</p>
        <p>{cached_code}</p>
        <p>Se você tiver alguma dúvida, sinta-se à vontade para entrar em contato conosco.</p>
        <p>Atenciosamente,<br>FlashVibe.</p>
    """
    plaintext_content = f"Olá, {name}!\nBem-vindo ao nosso serviço. Estamos felizes em tê-lo conosco."

    mail_body = {}
    mail_from = {
        "name": "Flash Vibe",
        "email": "MS_U7xQX5@trial-3yxj6lj7ex5ldo2r.mlsender.net",
    }

    recipients = [
        {
            "name": name,
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


# ------------------ View para validar código inserido pelo usuario na validação de email ---------------------     
@api_view(['POST'])
def Verify_confirmation_code(request):
        email = request.data.get('email')
        code = request.data.get('code')

        cached_code = cache.get(f'confirmation_code_{email}')

        if cached_code is None:
            return JsonResponse({'error': "No confirmation code found for this email."}, status=400)

        # Verificar o código no cache
        if cached_code and cached_code['email'] == email:
            if cached_code and cached_code['code'] == code:
                # Código correto, marque o e-mail como verificado
                try:
                    return JsonResponse({"message": "Email verified successfully."}, status=200)
                except:
                    return JsonResponse({"error": "User not found."}, status=404)
            else:
                return JsonResponse({"error": "Invalid or expired confirmation code."}, status=400)
        else:
            return JsonResponse({'error': "Invalid email or code for this request"})


# ------------------ View para logar o usuario e gerar o token de sessão ---------------------     
@api_view(['POST'])
def login_view(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return JsonResponse({'error': 'ID Token is required.'}, status=400)

    try:
        # Verifica o ID Token com Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Aqui você pode buscar ou criar um usuário Django associado ao UID do Firebase
        user, created = User.objects.get_or_create(username=uid)

        # Realiza o login do usuário
        login(request, user)

        # Cria um cookie de sessão
        response = JsonResponse({'message': 'User authenticated successfully.'})
        response.set_cookie('sessionid', request.COOKIES.get('sessionid'), httponly=True)

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
# ------------------ View para deslogar o usuario ---------------------     
@api_view(['POST'])
def logout_user(request):
    logout(request)  # Remove a sessão do usuário
    response = JsonResponse({'message': 'User logged out successfully.'})
    response.delete_cookie('sessionid')  # Opcional: remove o cookie de sessão
    return response

# ------------------ View para deletar um usuario do banco de dados ---------------------     
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    if request.method == 'DELETE':
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
    

# ------------------ View para atualizar algum dado do cliente ---------------------     
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_update(request):
    if request.method == 'PUT':
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

# ------------------ View para acessar o cadastro do usuario  ---------------------     
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_account(request):
    if request.method == 'GET':
            try:
                user = User.objects.get(pk=id)  # Usa o id recebido na URL
                serializer = UserSerializer(user)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
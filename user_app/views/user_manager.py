from rest_framework import status
from ..models import User
from rest_framework.response import Response
from ..serializers import UserSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.mail import EmailMultiAlternatives
from setup.settings import EMAIL_HOST_USER
from django.views.decorators.csrf import csrf_exempt
import hashlib
import time
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def make_custom_token(user):
    timestamp = str(int(time.time()))
    hash_string = f"{user.pk}-{timestamp}"
    token = hashlib.sha256(hash_string.encode()).hexdigest()
    return f"{token}-{timestamp}"
# ------------------ View para deletar um usuario do banco de dados ---------------------
@csrf_exempt     
@api_view(['DELETE'])
def user_delete(request):
    if request.method == 'DELETE':
            try:
                user = User.objects.get(pk=id) # recebe o id do usuario
                user = request.user # valida o cadastro completo do usuario
                if user.is_authenticated: # verifica se o usuario está autenticado
                    user.delete() # se estiver autenticado realiza a exclusão
                    return Response({"sucess": True, "message":"Usuário excluido com sucesso"}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({"sucess": False, "message":"Usuário não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                Response({"sucess": False, "message":"Usuário não está disponivel"}, status=status.HTTP_204_NO_CONTENT)
    

# ------------------ View para atualizar algum dado do cliente ---------------------     
@csrf_exempt
@api_view(['PUT'])
def user_update(request):
    if request.method == 'PUT':
            try:
                user = User.objects.get(pk=id) # recebe o id do usuario
                serializer = UserSerializer(user, data=request.data, partial=True) # salva os dados do usuario 
                if serializer.is_valid(raise_exception=True): 
                    serializer.save()
                    return Response(serializer.data, {"sucess": True, "message":"Usuário atualizado com sucesso"},status=status.HTTP_202_ACCEPTED)
            except User.DoesNotExist:
                return Response({"sucess": False, "message":"Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
            except ValidationError as e:

                return Response({"sucess": False, "message":{e}}, status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({"sucess": False, "message":"Metódo não autorizado"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@csrf_exempt
@api_view(['POST'])
def user_password_update(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"sucess": False, "message":"Email não encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # Gerar o token e enviar o email
    send_reset_email(user)
    return Response({"sucess": True, "message":"enviando email"}, status=status.HTTP_200_OK)


def send_reset_email(user):
    token = make_custom_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"http://localhost:3000/redefinir-senha?uid={uid}&token={token}"

    subject = "Flash vibe " 
    html_message = (f"""
        <p style="font-size:20px; color: #000;">Segue o link para redefinição de senha, se você não solicitou a troca de senha, desconsidere este link</p>
         <p style="display: inline-block;">
            <a href="{link}" style="background-color: #7fcfff; padding: 10px; border-radius: 5px; font-size: 24px; text-decoration: none; color: #000;">
                <strong>Redefinir Senha</strong>
            </a>
        </p>
        <p style="font-size:20px; color: #000;">Qualquer dúvida, entre em contato conosco.</p>
        """
    )
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=html_message,
        from_email=EMAIL_HOST_USER,
        to=[user.email],
    )
        
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()
    return Response({"sucess": True, "message":"email enviado com sucesso"}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def verify_reset_token(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')

    # Verifica se o token é válido
    if is_valid_token(uidb64, token):
        return Response({"sucess": True, "message":"Token válido"}, status=status.HTTP_200_OK)
    return Response({"sucess": False, "message":"Token inválido ou expirado!"}, status=status.HTTP_400_BAD_REQUEST)

def is_valid_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return False

    # Verifica se o token é válido para o usuário
    if(default_token_generator.check_token(user, token)):
        return Response({"sucess": True, "message":"Código verificado com sucesso"}, status=status.HTTP_200_OK) 


# ------------------ View para acessar o cadastro do usuario  ---------------------  
@csrf_exempt   
@api_view(['GET'])
def user_account(request):
    if request.method == 'GET':
            try:
                user = User.objects.get(pk=id)  # Usa o id recebido na URL
                serializer = UserSerializer(user)
                return Response(serializer.data, {"sucess": True, "message":"Usuário encontrado"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"sucess": False, "message":"Usuário não foi encontrado"}, status=status.HTTP_404_NOT_FOUND)
            except Exception:
                return Response({"sucess": False, "message":"Não foi possível validar o usuário"}, status=status.HTTP_400_BAD_REQUEST)
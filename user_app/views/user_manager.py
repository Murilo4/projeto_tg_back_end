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
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from setup.settings import EMAIL_HOST_USER

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
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_password_update(self, request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Email não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Gerar o token e enviar o email
    self.send_reset_email(user)
    return Response({"message": "Email enviado!"}, status=status.HTTP_200_OK)


def send_reset_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = f"https://localhost:3000/reset-password/?uid={uid}&token={token}"

    subject = "Flash vibe " 
    html_message = (f"""
        <p style="font-size:20px; color: #000;">Segue o link para redefinição de senha, se você não solicitou a troca de senha, desconsidere este link</p>
        <p style="display: inline-block;background-color: #7fcfff; padding: 10px; border-radius: 5px; font-size: 24px;">
            <strong>{link}</strong>
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
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    if reset_user_password(uidb64, token, new_password):
        return Response({"message": "Senha atualizada com sucesso!"}, status=status.HTTP_200_OK)
    return Response({"error": "Token inválido ou expirado!"}, status=status.HTTP_400_BAD_REQUEST)

def reset_user_password(uidb64, token, new_password):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return True
    return False

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
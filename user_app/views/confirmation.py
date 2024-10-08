from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..code_and_security.code_generator import generate_confirmation_code
from ..code_and_security.code_generator import generate_jwt, validate_jwt
from ..code_and_security.code_generator import generate_jwt_2
from django.core.cache import cache
from django.core import exceptions
from django.views.decorators.csrf import csrf_exempt
from setup.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
import re
import os
from ..models import User, TempRegistration
from ..serializers import TempUserSerializer
SECRET_KEY = os.getenv('SECRET_KEY')

# View para envio de código de confirmação de email ---------------------


@api_view(['POST'])
def validate_token_view(request):
    token = request.headers.get('Authorization')  # Obtém o token do cabeçalho

    if not token:
        return JsonResponse({"success": False,
                             "message": "Token JWT não encontrado."},
                            status=status.HTTP_401_UNAUTHORIZED)
    # Remove o prefixo 'Bearer ' se necessário
    if token.startswith('Bearer '):
        token = token[7:]
    # Valida o token JWT
    jwt_data = validate_jwt(token)

    if "error" in jwt_data:
        return JsonResponse({"success": False,
                             "message": jwt_data["error"]},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Se o token for válido
    return JsonResponse({"success": True,
                         "message": "Token válido."},
                        status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def confirmation_code(request) -> dict[str, str] | JsonResponse | None:
    try:
        nickname: str = request.data.get('nickname')
        email: str = request.data.get('email')
        name: str = request.data.get('name')

        errors = []  # Lista para coletar todos os erros
        if not nickname:
            return JsonResponse({"success": False,
                                 'message': 'usuario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return JsonResponse({"success": False,
                                 'message': 'Email invalido'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Validação do nome de usuário
        if User.objects.filter(nick_name=nickname).exists():
            errors.append(
                "nickname já existe")
        if len(nickname) < 2:
            errors.append(
                "nickname muito pequeno")
        elif len(nickname) > 50:
            errors.append(
                "nickname muito grande")

        # Validação do email

        if User.objects.filter(email=email).exists():
            errors.append(
                "Email já registrado")

        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return JsonResponse({
                "success": False,
                "message": "Email não é válido"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Se houver erros, retorne a lista de erros
        if errors:
            return JsonResponse({
                "success": False,
                "message": errors  # Retorna todos os erros encontrados
            }, status=status.HTTP_400_BAD_REQUEST)
        try:

            # Prepara os dados do usuário temporário para o serializer
            user_temp_format = {'nick_name': nickname,
                                'user_name':  name,
                                'email': email}
            user_to_code = {'username': name,
                            'email': email}

            # Usar o serializer para validar e criar o registro temporário
            serializer = TempUserSerializer(data=user_temp_format)
            if serializer.is_valid():
                user_temp = serializer.save()  # Salva o usuário temporário
                cache.set(f'usuario_{email}', user_temp_format, timeout=300)
                # Gera o JWT para o usuário
                jwt_token = generate_jwt(user_temp)

                send_email_code(user_to_code, jwt_token)
                return JsonResponse({
                    "success": True,
                    "message": "Dados confirmados, email enviado.",
                    "jwt_token": jwt_token
                }, status=status.HTTP_200_OK)

                # Se o serializer não for válido, retorne os erros
            return JsonResponse({
                "success": False,
                "message": "usuario temporario já existe"
            }, status=status.HTTP_400_BAD_REQUEST)

        except exceptions.BadRequest:  # Captura exceção com informações
            return JsonResponse({
                "success": False,
                "message": 'Erro ao salvar os dados'
                }, status=status.HTTP_400_BAD_REQUEST)
    except exceptions.FieldDoesNotExist:
        return JsonResponse({"success": False,
                            "message":
                             "Não foi possível realizar a validação"},
                            status=status.HTTP_400_BAD_REQUEST)


def send_email_code(user_to_code, token=None):
    try:
        email = user_to_code['email']
        name = user_to_code['username']
        token = token
        generate_code = generate_confirmation_code()

        verification_data = {'code': generate_code, 'email': email}
        cache.set(f'confirmation_code_{email}', verification_data, timeout=300)

        formatted_code = " ".join(generate_code)
        subject = "Flash vibe codigo de confirmação "
        html_message = f"""
        <p style="font-size:20px; color: #000;">
        <strong>{name}</strong>,</p>
        <p style="font-size:20px; color: #000;">
        Obrigado por se registrar! Agora confirmaremos seu e-mail.</p>
        <p style="font-size:20px; color: #000;">
        Insira o código no campo que foi solicitado:</p>
        <p style="display: inline-block;background-color: #D3D3D3;
        padding: 10px; border-radius: 5px; font-size: 24px;">
            <strong>{formatted_code}</strong>
        </p>
        <p style="font-size:20px; color: #000;">Qualquer dúvida,
        entre em contato conosco.</p>
        """

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=EMAIL_HOST_USER,
            to=[email],
        )
        email_message.attach_alternative(html_message, "text/html")

        if email_message.send():
            # Check if the email was sent successfully
            return JsonResponse({
                "success": True,
                "message": "email enviado com sucesso"
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "success": False,
                "message": "não foi possível enviar o email"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except exceptions.BadRequest:
        return JsonResponse({
            "success": False,
            "message": "Erro ao enviar email"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View para validar código inserido pelo usuario na validação de email ------


@api_view(['post'])
def resend_email_code(request):
    try:
        email = request.data.get('email')

        cache.get(f'confirmation_code_{email}')
        user = TempRegistration.objects.get(email=email)

        user_data = {
                    "email": user.email,
                    "user_name": user.user_name,
                    }
        if user_data:
            send_email_code(user_data)
            return JsonResponse({"success": True,
                                "message":
                                    "Email de confirmação enviado novamente"},
                                status=status.HTTP_200_OK
                                )
    except exceptions.ObjectDoesNotExist:
        return JsonResponse(
            {"success": False,
                "message": "Não foi possível encontrar o usuário"},
            status=status.HTTP_404_NOT_FOUND
            )
    except exceptions.ValidationError:
        return JsonResponse(
            {"success": False, 
             "message": "Erro ao validar o código de confirmação"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except exceptions.BadRequest:
        return JsonResponse({"success": False,
                            "message":
                                "Não foi possível realizar o reenvio"},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def Verify_confirmation_code(request):
    email = request.data.get('email')
    code = request.data.get('code')

    cached_code = cache.get(f'confirmation_code_{email}')
    if not code:
        return JsonResponse({"success": False,
                            'message': 'nenhum codigo identificado'},
                            status=status.HTTP_400_BAD_REQUEST)
    if not email:
        return JsonResponse({"success": False,
                            'message': 'Email invalido'},
                            status=status.HTTP_400_BAD_REQUEST)
    try:
        user = TempRegistration.objects.get(email=email)
    except TempRegistration.DoesNotExist:
        return JsonResponse({"success": False,
                             "message": "Usuário temporário não encontrado."},
                            status=status.HTTP_404_NOT_FOUND)

    if cached_code is None:
        return JsonResponse({
            'success': False,
            "message":
            "Nenhum código de confirmação encontrado para este email"},
            status=status.HTTP_400_BAD_REQUEST)
    try:
        # Verificar o código no cache
        if cached_code and cached_code['email'] == email:
            if cached_code and cached_code['code'] == code:
                # Código correto, marque o e-mail como verificado
                try:
                    cache.delete(f'confirmation_code_{email}')
                    user_data = {
                        "email": user.email,
                        "user_name": user.user_name,
                        "nick_name": user.nick_name
                    }
                    jwt_token = generate_jwt_2(user_data)
                    return JsonResponse({
                        "success": True,
                        "message": "Email verified successfully.",
                        "jwt_token": jwt_token},
                        status=status.HTTP_200_OK)

                except exceptions.ObjectDoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "message": "Usuário não encontrado."},
                        status=status.HTTP_404_NOT_FOUND)
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Código invalido ou expirado."},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({
                "success": False,
                "message":
                "Email ou código invalido para essa requisição."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)

    except exceptions.ViewDoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "erro inesperado ocorreu"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

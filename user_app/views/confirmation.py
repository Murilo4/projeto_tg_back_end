from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..code_generator import generate_confirmation_code
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from setup.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.core import exceptions
import re
from ..models import User


# View para envio de código de confirmação de email ---------------------
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request) -> dict[str, str] | JsonResponse | None:
    try:
        username: str = request.data.get('name')
        email: str = request.data.get('email')
        errors = []  # Lista para coletar todos os erros
        if not username:
            return JsonResponse({"success": False,
                                 'message': 'usuario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return JsonResponse({"success": False,
                                 'message': 'Email invalido'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Validação do nome de usuário
        if User.objects.filter(user_name=username).exists():
            errors.append(
                "Usuário já existe")
        if len(username) < 2:
            errors.append(
                "Nome muito pequeno")
        elif len(username) > 50:
            errors.append(
                "Nome muito grande")

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

        user_to_code = {'username': username, 'email': email}
        if not errors:
            send_email_code(user_to_code)
            return JsonResponse({
                "success": True,
                "message": "Dados confirmados, enviado email"},
                status=status.HTTP_200_OK)
    except exceptions.BadRequest:
        return JsonResponse({"success": False,
                            "message":
                                "Não foi possível realizar a validação"},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['post'])
def resend_email_code(request):
    try:
        username = request.data.get('name')
        email = request.data.get('email')
        if not username:
            return JsonResponse({"success": False,
                                'message': 'usuario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return JsonResponse({"success": False,
                                'message': 'Email invalido'},
                                status=status.HTTP_400_BAD_REQUEST)

        if username and email:
            user_to_code = {'username': username, 'email': email}
            send_email_code(user_to_code)
            return JsonResponse({"success": True,
                                "message":
                                    "Email de confirmação enviado novamente"},
                                status=status.HTTP_200_OK
                                )

    except exceptions.BadRequest:
        return JsonResponse({"success": False,
                            "message":
                                "Não foi possível realizar o reenvio"},
                            status=status.HTTP_400_BAD_REQUEST)


def send_email_code(user_to_code):
    try:
        email = user_to_code['email']
        name = user_to_code['username']
        generate_code = generate_confirmation_code()

        verification_data = {'code': generate_code, 'email': email}
        cache.set(f'confirmation_code_{email}', verification_data, timeout=180)

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

        if email_message.send():  # Check if the email was sent successfully
            return JsonResponse({
                "success": True,
                "message": "email enviado com sucesso"
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "success": False,
                "message": "não foi possível enviar o email"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Erro ao enviar email: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View para validar código inserido pelo usuario na validação de email ------


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
                    return JsonResponse({
                        "success": True,
                        "message": "Email verified successfully."},
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

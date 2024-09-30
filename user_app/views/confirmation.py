from ast import type_ignore
from typing import Any
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..code_generator import generate_confirmation_code
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from setup.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.core import exceptions
import re


# ------------------ View para envio de código de confirmação de email ---------------------      
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request) -> JsonResponse:
    try:
        generate_code = generate_confirmation_code()
        email = request.data.get('email')
        name = request.data.get('name')

        # Validate the email address using re
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email):
            return JsonResponse({
                "success": False,
                "message": "Email address is not valid"
            }, status=status.HTTP_400_BAD_REQUEST)

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

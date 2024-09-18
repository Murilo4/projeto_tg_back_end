from rest_framework import status
from ..models import User
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..code_generator import generate_confirmation_code
from django.core.cache import cache
from mailersend import emails
from dotenv import load_dotenv
import os
from django.views.decorators.csrf import csrf_exempt

load_dotenv()
         
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
    subject = "Bem-vindo ao flash Vibe!"
    html_content = f"""
        <h1>Olá, {name}!</h1>
        <p>Bem-vindo ao nosso serviço.</p>
        <p>Estamos felizes em tê-lo conosco.</p>
        <p>O código de segurança de 6 digitos para confirmação do endereço de email:</p>
        <p>{cached_code}</p>
        <p>Se você tiver alguma dúvida, sinta-se à vontade para entrar em contato conosco.</p>
        <p>Atenciosamente,<br>Flash Vibe.</p>
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





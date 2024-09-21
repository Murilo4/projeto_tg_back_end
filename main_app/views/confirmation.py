from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..code_generator import generate_confirmation_code
from django.core.cache import cache
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from setup.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives

load_dotenv()
         
# ------------------ View para envio de código de confirmação de email ---------------------      
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request):
    try:
        generate_code = generate_confirmation_code()
        email = request.data.get('email')
        name = request.data.get('name')
        verification_data = {
        'code': generate_code,
        'email': email
    }
        cache.set(f'confirmation_code_{email}', verification_data,  timeout=300)
        # Manually open the connection

        formatted_code = " ".join(generate_code)
        subject = "Flash vibe codigo de confirmação " 
        html_message = (f"""
        <p style="font-size:20px; color: #000;"><strong>{name}</strong>,</p>
        <p style="font-size:20px; color: #000;">Obrigado por se registrar! Agora confirmaremos seu e-mail.</p>
        <p style="font-size:20px; color: #000;">Insira o código no campo que foi solicitado:</p>
        <p style="display: inline-block;background-color: #D3D3D3; padding: 10px; border-radius: 5px; font-size: 24px;">
            <strong>{formatted_code}</strong>
        </p>
        <p style="font-size:20px; color: #000;">Qualquer dúvida, entre em contato conosco.</p>
        """
        )
        email_message = EmailMultiAlternatives(
        subject=subject,
        body=html_message,
        from_email=EMAIL_HOST_USER,
        to=[email],
        )
        
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        # Captura e imprime a exceção
        print(str(e))  # Para debug, você pode registrar isso em um log
        return JsonResponse({"error": "An error occurred: " + str(e)}, status=500)

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





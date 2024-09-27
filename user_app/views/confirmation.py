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
from django.http import JsonResponse

load_dotenv()
         
# ------------------ View para envio de código de confirmação de email ---------------------      
@csrf_exempt
@api_view(['POST'])
def confirmation_code(request):
    try:
        generate_code = generate_confirmation_code() # chama a função de geração de codigo
        email = request.data.get('email') # recebe o email do front end
        name = request.data.get('name')  # recebe o nome do front end
        verification_data = { # armazena o codigo e o email 
        'code': generate_code, 
        'email': email
    }
        cache.set(f'confirmation_code_{email}', verification_data,  timeout=300) # salva o email e o código no cache do django
        # Manually open the connection

        formatted_code = " ".join(generate_code) # forma o codigo para visualização no email
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
        ) # estrutura para o envio do email
        
        email_message.attach_alternative(html_message, "text/html")
        email_message.send() # envia o email
        return JsonResponse({"sucess": True, "message":"email enviado com sucesso"}, status=status.HTTP_200_OK) # retorna a resposta, com a mensagem de envio e o status
    except Exception as e:
        # Captura e imprime a exceção
        return JsonResponse({"sucess": False, "message": "não foi possivel enviar o email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # retorna o erro que não foi possivel enviar

# ------------------ View para validar código inserido pelo usuario na validação de email ---------------------     

@api_view(['POST'])
def Verify_confirmation_code(request):
        email = request.data.get('email') # recebe o email do front end
        code = request.data.get('code') # recebe o codigo do front end

        cached_code = cache.get(f'confirmation_code_{email}') # pega o email do cache do django

        if cached_code is None: # se não for encontrado o código será retornado que o codigo é invalido
            return JsonResponse({'sucess': False, "message": "Nenhum código de confirmação encontrado para este email"}, status=status.HTTP_400_BAD_REQUEST) 
        try:
            # Verificar o código no cache
            if cached_code and cached_code['email'] == email: # valida se o email está correto
                if cached_code and cached_code['code'] == code: # valida se o codigo está correto
                    # Código correto, marque o e-mail como verificado
                    try:
                        return JsonResponse({"sucess": True, "message":"Email verified successfully."}, status=status.HTTP_200_OK)
                    except:
                        return JsonResponse({"sucess": False,"message":"Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return JsonResponse({"sucess": False, "message":"Código invalido ou expirado."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return JsonResponse({"sucess": False, "message":"Email ou código invalido para essa requisição."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return JsonResponse({"sucess": False, "message": "erro inesperado ocorreu"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






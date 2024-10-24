from ..models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from firebase_admin import auth
from django.contrib.auth import logout
from rest_framework import status
from django.core import exceptions
from ..code_and_security.code_generator import generate_session_id
from ..code_and_security.code_generator import generate_jwt_session
from ..code_and_security.code_generator import blacklist_jwt
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import credentials
import firebase_admin
from django.core.cache import cache
import requests
import os
from django.core.exceptions import ValidationError
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
})
firebase_admin.initialize_app(cred)


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    if request.method == "POST":
        id_token = request.data.get('id_token')
        email = request.data.get('email')
        try:
            if id_token is None:
                return JsonResponse({"success": False,
                                    "message": "id token não localizado"},
                                    status=status.HTTP_404_NOT_FOUND)

            if email is None:
                return JsonResponse({"success": False,
                                    "message": "email não localizado"},
                                    status=status.HTTP_404_NOT_FOUND)
                # Verifica e decodifica o token do Firebase
                # decoded_token = auth.verify_id_token(id_token)
                # if decoded_token:
                # Extrai o e-mail diretamente do token
            user = User.objects.get(email=email)

            jwt_token = generate_jwt_session(user)
            # Gera um cookie de sessão
            session_id = generate_session_id()
            cache.set(f'user_auth_{session_id}', email, timeout=604800)

            response = JsonResponse({'success': True,
                                    'message':
                                    'Login realizado com sucesso',
                                    'cookie': session_id,
                                    'jwt_token': jwt_token,
                                    'email': email})
            response.set_cookie('session_id', session_id, max_age=604800)
            return response

        except auth.InvalidIdTokenError:
            return JsonResponse({'success': False,
                                'message': 'Token inválido'},
                                status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return JsonResponse({'success': False,
                                'message': 'Usuario não localizado'},
                                status=status.HTTP_404_NOT_FOUND)
    # else:
    #    return JsonResponse({"success": False,
    #                         "message":  "Método não permitido"},
    #                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def logout_user(request):
    if request.method == 'POST':
        session_id = request.COOKIES.get('session_id')
        try:
            middleware_response = SessaologoutMiddleware(session_id)
            if isinstance(middleware_response, JsonResponse):
                return JsonResponse({'sucess': False,
                                    'message': 'Usuario não está logado'},
                                    status=status.HTTP_400_BAD_REQUEST)
            logout(request)
            response = requests.post(
                f'http://ec2-54-94-30-193.sa-east-1.compute.amazonaws.com:8000/validate-token/')
            if response.status_code == 404:
                raise ValidationError(f'Não foi possivel validar o token.')

            token = request.headers.get('Authorization')
            if token.startswith("Bearer "):
                token = token[7:]

            blacklist_jwt(token)
            # Remove a sessão do usuário
            response = JsonResponse({
                'success': True,
                'message': 'Usuario deslogado'},
                status=status.HTTP_200_OK)
            response.delete_cookie('session_id')
            return response
        except exceptions.PermissionDenied:
            JsonResponse({
                "success": False,
                "message": "não foi possivel encontrar nenhuma sessão"},
                status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"success": False,
                             "message": "Metodo não autorizado?"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def validate_session(request):
    session_id = request.COOKIES.get('session_id')
    print(session_id)
    if not session_id:
        return JsonResponse({'success': False,
                            'message': 'Nenhum token de sessão encontrado'},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Verifica se a sessão está no cache
    user_id = cache.get(f'user_auth_{session_id}')

    if user_id:
        # Sessão válida
        return JsonResponse({'success': True,
                            'message': 'Sessão válida',
                             'user_id': user_id})
    else:
        # Sessão inválida ou expirada
        return JsonResponse({'success': False,
                            'error': 'Sessão inválida ou expirada'},
                            status=status.HTTP_401_UNAUTHORIZED)


def SessaologoutMiddleware(session_id):
    if not session_id:  # Verifica se session_id é None ou uma string vazia
        return JsonResponse({'success': False,
                             'message': 'Usuário não está logado!'},
                            status=status.HTTP_401_UNAUTHORIZED)

    return True

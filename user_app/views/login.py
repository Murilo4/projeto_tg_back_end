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
    "auth_provider_x509_cert_url": os.getenv(
        "FIREBASE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
})
firebase_admin.initialize_app(cred)


@csrf_exempt
@api_view(['POST'])
def login_view_email(request):
    if request.method == "POST":
        id_token = request.data.get('id_token')
        email = request.data.get('email')
        try:
            if id_token is None:
                return JsonResponse({"success": False,
                                    "error": ["id token não localizado"]},
                                    status=status.HTTP_404_NOT_FOUND)

            if email is None:
                return JsonResponse({"success": False,
                                    "error": ["email não localizado"]},
                                    status=status.HTTP_404_NOT_FOUND)
                # Verifica e decodifica o token do Firebase
            decoded_token = auth.verify_id_token(id_token)
            if decoded_token:
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
                                        'Authorization': jwt_token,
                                        'email': email})
                response.set_cookie('Authorization', jwt_token, max_age=604800)
                response.set_cookie('session_id', session_id, max_age=604800)
                return response

        except auth.InvalidIdTokenError:
            return JsonResponse({'success': False,
                                'error': ['Token inválido']},
                                status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return JsonResponse({'success': False,
                                'error': ['Usuario não localizado']},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({"success": False,
                            "error":  ["Método não permitido"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def login_view_phone(request):
    if request.method == "POST":
        id_token = request.data.get('id_token')
        phone = request.data.get('phone')
        try:
            if id_token is None:
                return JsonResponse({"success": False,
                                    "error": ["id token não localizado"]},
                                    status=status.HTTP_404_NOT_FOUND)

            if phone is None:
                return JsonResponse({"success": False,
                                    "error": ["telefone não localizado"]},
                                    status=status.HTTP_404_NOT_FOUND)
                # Verifica e decodifica o token do Firebase
            decoded_token = auth.verify_id_token(id_token)
            if decoded_token:
                # Extrai o e-mail diretamente do token
                user = User.objects.get(phone=phone)

                jwt_token = generate_jwt_session(user)
                # Gera um cookie de sessão
                session = generate_session_id()
                cache.set(f'user_auth_{session}', phone, timeout=604800)

                response = JsonResponse({'success': True,
                                        'message':
                                         'Login realizado com sucesso',
                                         'cookie': session,
                                         'Authorization': jwt_token,
                                         'phone': phone})
                response.set_cookie('Authorization', jwt_token,
                                    max_age=604800, secure=True,
                                    samesite='None')
                response.set_cookie('session', session,
                                    max_age=604800, secure=True,
                                    samesite='None')
                return response

        except auth.InvalidIdTokenError:
            return JsonResponse({'success': False,
                                'error': ['Token inválido']},
                                status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return JsonResponse({'success': False,
                                'error': ['Usuario não localizado']},
                                status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({"success": False,
                            "error":  ["Método não permitido"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(["POST"])
def logout_user(request):
    if request.method == 'POST':
        try:
            session_id = request.headers.get('session')
            if not session_id:
                return JsonResponse({"success": False,
                                     "error": "Não está logado"},
                                    status=status.HTTP_401_UNAUTHORIZED)

            cache.delete(f'user_auth_{session_id}')

            token = request.headers.get('Authorization')
            blacklist_jwt(token)

            return JsonResponse({
                'success': True,
                'message': ['Usuário deslogado']},
                status=status.HTTP_200_OK)
        except exceptions.PermissionDenied:
            return JsonResponse({
                "success": False,
                "error": ["Não foi possível encontrar nenhuma sessão"]},
                status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"success": False,
                             "error": ["Método não autorizado"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def validate_session(request):
    session = request.data.get('session')

    if session is None:
        return JsonResponse({'success': False,
                            'error': ['Nenhum token de sessão encontrado']},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Verifica se a sessão está no cache
    user_id = cache.get(f'user_auth_{session}')

    if user_id:
        # Sessão válida
        return JsonResponse({'success': True,
                            'message': ['Sessão válida'],
                             'user_id': user_id})
    else:
        # Sessão inválida ou expirada
        return JsonResponse({'success': False,
                            'error': ['Sessão inválida ou expirada']},
                            status=status.HTTP_401_UNAUTHORIZED)


def SessaologoutMiddleware(session_id):
    if not session_id:  # Verifica se session_id é None ou uma string vazia
        return JsonResponse({'success': False,
                             'error': ['Usuário não está logado!']},
                            status=status.HTTP_401_UNAUTHORIZED)

    return True

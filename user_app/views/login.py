import time
from ..models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from firebase_admin import auth
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
from django.core import exceptions
from ..code_and_security.code_generator import generate_session_id
from django.contrib.auth.models import User
from firebase_admin import credentials
import firebase_admin
from django.core.cache import cache
cred = credentials.Certificate('user_app/conections/firebase.json')
firebase_admin.initialize_app(cred)


@api_view(['POST'])
def login_view(request):
    id_token = request.POST.get('id_token')

    try:
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        user = User.objects.get(id=user_id)
        if user:
            # Gera um cookie de sessão
            session_id = generate_session_id()
            cache.set(f'user_auth_{session_id}', session_id, timeout=604800)
            response = JsonResponse({'cookie': session_id})
            response.set_cookie('session_id', session_id, max_age=604800)  # 604800 segundos = 7 dias

            return response
    except auth.InvalidIdTokenError:
        return JsonResponse({'error': 'Token inválido'}, status=401)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=404)
    # except:
    #     return JsonResponse({'error': 'Usuário não encontrado'}, status=404)


@api_view(['POST'])
def logout_user(request):
    if SessaologoutMiddleware:
        logout(request)
        try:  # Remove a sessão do usuário
            response = JsonResponse({
                'success': True,
                'message': 'User logged out successfully.'},
                status=status.HTTP_200_OK)
            response.delete_cookie('sessionid')
            return response
        except exceptions.PermissionDenied:
            Response({
                "success": False,
                "message": "não foi possivel encontrar nenhuma sessão"},
                status=status.HTTP_204_NO_CONTENT)


def authenticate_session(session_id):
    # Verificar se o cookie de sessão é válido
    # Retorna o usuário autenticado ou None se não for válido
    user = User.objects.filter(session_id=session_id).first()
    if user:
        return user
    return None


@api_view(['POST'])
def validate_session(request):
    session_id = request.COOKIES.get('session_id')

    if not session_id:
        return JsonResponse({'success': False,
                            'message': 'Nenhum token de sessão encontrado'},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Verifica se a sessão está no cache
    user_id = cache.get(session_id)

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


class SessaologoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'session_id' not in request.COOKIES:
            return JsonResponse({'success': False,
                                 'message': 'Acesso negado!'},
                                status=status.HTTP_401_UNAUTHORIZED)

        # Verificar se o cookie de sessão é válido
        session_id = request.COOKIES['session_id']
        user = authenticate_session(session_id)
        if user is None:
            return JsonResponse('Acesso negado!',
                                status=status.HTTP_401_UNAUTHORIZED)

        # Se o usuário está autenticado, permitir o logout
        if request.method == 'POST' and request.path == '/logout/':
            logout_user(request, user)

        return self.get_response(request)

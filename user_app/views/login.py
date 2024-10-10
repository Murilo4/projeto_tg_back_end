from ..models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from firebase_admin import auth
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
from django.core import exceptions
from ..code_and_security.code_generator import generate_session_id
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from firebase_admin import credentials
import firebase_admin
from django.core.cache import cache
cred = credentials.Certificate('user_app/conections/firebase.json')
firebase_admin.initialize_app(cred)


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    id_token = request.data.get('id_token')

    try:
        if id_token is not None:

            # Gera um cookie de sessão
            session_id = generate_session_id()
            cache.set(f'user_auth_{session_id}', session_id, timeout=300)
            response = JsonResponse({'success': True,
                                    'message': 'Login realizado com sucesso',
                                     'session_id': session_id})

            response.set_cookie('session_id', session_id, max_age=300, httponly=True, samesite='None')

            return response
    except auth.InvalidIdTokenError:
        return JsonResponse({'success': False,
                            'message': 'Token inválido'},
                            status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return JsonResponse({'success':  False,
                            'message': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def logout_user(request):
    session_id = request.COOKIES.get('session_id')
    print(session_id)
    try:
        middleware_response = SessaologoutMiddleware(session_id)
        if isinstance(middleware_response, JsonResponse):
            return JsonResponse({'sucess': False,
                                 'message': 'Usuario não está logado'},
                                status=status.HTTP_400_BAD_REQUEST)
        logout(request)
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
    print('este é o idtoken', session_id)

    if not session_id:  # Verifica se session_id é None ou uma string vazia
        return JsonResponse({'success': False, 'message': 'Usuário não está logado!'},
                            status=status.HTTP_401_UNAUTHORIZED)

    # Se chegou aqui, session_id é válido
    return True  # Você pode retornar True para indicar que o usuário está logado

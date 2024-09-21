from ..models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from firebase_admin import auth
from django.contrib.auth import login
from django.contrib.auth import logout

# ------------------ View para logar o usuario e gerar o token de sessão ---------------------     
@api_view(['POST'])
def login_view(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return JsonResponse({'error': 'ID Token is required.'}, status=400)

    try:
        # Verifica o ID Token com Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Aqui você pode buscar ou criar um usuário Django associado ao UID do Firebase
        user, created = User.objects.get_or_create(username=uid)

        # Realiza o login do usuário
        login(request, user)

        # Cria um cookie de sessão
        response = JsonResponse({'message': 'User authenticated successfully.'})
        response.set_cookie('sessionid', request.COOKIES.get('sessionid'), httponly=True)

        return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
# ------------------ View para deslogar o usuario ---------------------     
@api_view(['POST'])
def logout_user(request):
    logout(request)  # Remove a sessão do usuário
    response = JsonResponse({'message': 'User logged out successfully.'})
    response.delete_cookie('sessionid')  # Opcional: remove o cookie de sessão
    return response
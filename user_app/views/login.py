from ..models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from firebase_admin import auth
from django.contrib.auth import login
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
# ------------------ View para logar o usuario e gerar o token de sessão ---------------------     
@api_view(['POST'])
def login_view(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return Response({"sucess": False, "message":"token id é necessário "}, status=status.HTTP_204_NO_CONTENT)

    try:
        # Verifica o ID Token com Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Aqui você pode buscar ou criar um usuário Django associado ao UID do Firebase
        user, created = User.objects.get_or_create(username=uid)

        # Realiza o login do usuário
        login(request, user)

        # Cria um cookie de sessão
        response = Response({"sucess": True, 'message': 'Usuário autenticado com sucesso'}, status=status.HTTP_200_OK)
        response.set_cookie('sessionid', request.COOKIES.get('sessionid'), httponly=True)

        return response

    except Exception:
        return Response({"sucess": False, "message":"um erro inesperado ocorreu"})
    
# ------------------ View para deslogar o usuario ---------------------     
@api_view(['POST'])
def logout_user(request):
    logout(request)
    try:  # Remove a sessão do usuário
        response = JsonResponse({'message': 'User logged out successfully.'})
        response.delete_cookie('sessionid')  # Opcional: remove o cookie de sessão
        return response
    except:
        Response({"sucess": False, "message":"não foi possivel encontrar nenhuma sessão"}, status=status.HTTP_204_NO_CONTENT)
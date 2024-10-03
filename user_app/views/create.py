from rest_framework import status
from ..serializers import UserSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import User, TempRegistration
from django.core import exceptions
from ..code_and_security.code_generator import validate_jwt

# ------------------ View para criação de usuario ---------------------


@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({"success": False,
                                 "message": "Token não encontrado."},
                                status=status.HTTP_401_UNAUTHORIZED)

        if token.startswith("Bearer "):
            token = token[7:]

        jwt_data = validate_jwt(token)

        if 'error' in jwt_data:
            return JsonResponse({"success": False,
                                 "message": jwt_data['error']},
                                status=status.HTTP_401_UNAUTHORIZED)

        email = jwt_data.get('email')
        temp_user = TempRegistration.objects.filter(email=email).first()

        if not temp_user:
            return JsonResponse({"success": False,
                                 "message":
                                 "Usuário temporário não encontrado."},
                                status=status.HTTP_404_NOT_FOUND)

        username = temp_user.user_name
        nickname = temp_user.nick_name
        errors = []  # Lista para coletar todos os erros
        if not username:
            return JsonResponse({"success": False,
                                 'message': 'usuario invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return JsonResponse({"success": False,
                                 'message': 'Email invalido'},
                                status=status.HTTP_400_BAD_REQUEST)
        # Validação do nome de usuário
        if User.objects.filter(user_name=username).exists():
            errors.append(
                "Usuário já existe")
        if len(username) < 2:
            errors.append(
                "Nome muito pequeno")
        elif len(username) > 50:
            errors.append(
                "Nome muito grande")

        # Validação do email

        if User.objects.filter(email=email).exists():
            errors.append(
                "Email já registrado")

        # Se houver erros, retorne a lista de erros
        if errors:
            return JsonResponse({
                "success": False,
                "message": errors  # Retorna todos os erros encontrados
            }, status=status.HTTP_400_BAD_REQUEST)
        new_user_dict = {'user_name': username, 'email': email,
                         'nick_name': nickname}
        
        user_formated = {'username': username, 'email': email,
                         'nickname': nickname}
        serializer = UserSerializer(data=new_user_dict)
        serializer.is_valid()
        temp_user = serializer.save()  # salva o usuario no banco de dados
        return JsonResponse({
            "success": True,
            "message": "Usuário criado com sucesso",
            "data": user_formated},
            status=status.HTTP_201_CREATED)
    except exceptions.BadRequest:
        return JsonResponse({"success": False,
                            "message":
                                "Não foi possível realizar a criação"},
                            status=status.HTTP_400_BAD_REQUEST)

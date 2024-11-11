from rest_framework import status
from ..serializers import UserSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import User, TempRegistration
from django.core import exceptions
from ..code_and_security.code_generator import validate_jwt
import re

# ------------------ View para criação de usuario ---------------------


@csrf_exempt
@api_view(['POST'])
def create_user(request):
    if request.method == "POST":
        try:
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({"success": False,
                                    "error": ["Token não encontrado."]},
                                    status=status.HTTP_401_UNAUTHORIZED)

            if token.startswith("Bearer "):
                token = token[7:]

            jwt_data = validate_jwt(token)

            if 'error' in jwt_data:
                return JsonResponse({"success": False,
                                    "error": jwt_data['error']},
                                    status=status.HTTP_401_UNAUTHORIZED)

            email = jwt_data.get('email')
            temp_user = TempRegistration.objects.filter(email=email).first()

            if not temp_user:
                return JsonResponse({"success": False,
                                    "error":
                                     ["Usuário temporário não encontrado."]},
                                    status=status.HTTP_404_NOT_FOUND)

            nickname = temp_user.nick_name
            username = temp_user.user_name
            errors = []  # Lista para coletar todos os erros
            if not username:
                return JsonResponse({"success": False,
                                    'error': ['usuario invalido']},
                                    status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return JsonResponse({"success": False,
                                    'error': ['Email invalido']},
                                    status=status.HTTP_400_BAD_REQUEST)
            # Validação do nome de usuário
            if User.objects.filter(nick_name=nickname).exists():
                errors.append(
                    "nickname já existe")

            # Validação do email

            if User.objects.filter(email=email).exists():
                errors.append(
                    "Email já registrado")

            pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(pattern, email):
                return JsonResponse({
                    "success": False,
                    "error": ["Email não é válido"]
                }, status=status.HTTP_400_BAD_REQUEST)

            # Se houver erros, retorne a lista de erros
            if errors:
                return JsonResponse({
                    "success": False,
                    "error": errors  # Retorna todos os erros encontrados
                }, status=status.HTTP_400_BAD_REQUEST)

            new_user_dict = {'user_name': username, 'email': email,
                             'nick_name': nickname}

            serializer = UserSerializer(data=new_user_dict)
            serializer.is_valid()
            temp_user = serializer.save()  # salva o usuario no banco de dados

            return JsonResponse({
                "success": True,
                "message": ["Usuário criado com sucesso"],
                "email": email},
                status=status.HTTP_201_CREATED)

        except exceptions.BadRequest:
            return JsonResponse({"success": False,
                                "error":
                                    ["Não foi possível realizar a criação"]},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"success": False,
                             "error": ["Metodo não permitido"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['POST'])
def create_user_from_social(request):
    if request.method == "POST":
        try:
            email = request.data.get("email")
            username = request.data.get("username")
            nickname = request.data.get("nickname")

            errors = []  # Lista para coletar todos os erros
            if not username:
                return JsonResponse({"success": False,
                                    'error': ['usuario invalido']},
                                    status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return JsonResponse({"success": False,
                                    'error': ['Email invalido']},
                                    status=status.HTTP_400_BAD_REQUEST)
            if not nickname:
                return JsonResponse({"success": False,
                                     'error': ['Nickname invalido']},
                                    status=status.HTTP_400_BAD_REQUEST)
            
            # Validação do nome de usuário
            if User.objects.filter(nick_name=nickname).exists():
                errors.append(
                    "nickname já existe")

            # Validação do email

            if User.objects.filter(email=email).exists():
                errors.append(
                    "Email já registrado")

            # Se houver erros, retorne a lista de erros
            if errors:
                return JsonResponse({
                    "success": False,
                    "error": [errors]  # Retorna todos os erros encontrados
                }, status=status.HTTP_400_BAD_REQUEST)

            new_user_dict = {'user_name': username, 'email': email,
                             'nick_name': nickname}

            serializer = UserSerializer(data=new_user_dict)
            serializer.is_valid()
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            return JsonResponse({
                "success": True,
                "message": ["Usuário criado com sucesso"]},
                status=status.HTTP_201_CREATED)

        except exceptions.BadRequest:
            return JsonResponse({"success": False,
                                "error":
                                    ["Não foi possível realizar a criação"]},
                                status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"success": False,
                             "error": ["Metodo não permitido"]},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

from rest_framework import status
from ..serializers import UserSerializer
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import User

# ------------------ View para criação de usuario ---------------------
@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        new_user = request.data # recebe os dados do front end
        username = new_user.get('user_name')
        errors = []  # Lista para coletar todos os erros

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
        email = new_user.get('email')
        if User.objects.filter(email=email).exists():
            errors.append(
                "Email já registrado")

        # Se houver erros, retorne a lista de erros
        if errors:
            return JsonResponse({
                "success": False,
                "message": errors  # Retorna todos os erros encontrados
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=new_user) # armazena os dados com o serializer
        serializer.is_valid() # valida se os dados estão corretos com o serializer, se estiver errado vai soltar a excessão
        new_user = serializer.save() # salva o usuario no banco de dados
        return JsonResponse({
            "success": True, 
            "message": "Usuário criado com sucesso"},
            status=status.HTTP_201_CREATED) # retorna para o front end os dados salvos, uma mensagem de sucesso e o status
    except:
        return JsonResponse({"success": False,
                              "message": "Não foi possível realizar a criação da conta"}, 
                              status=status.HTTP_400_BAD_REQUEST) # retorna a excessão
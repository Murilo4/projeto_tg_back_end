from rest_framework import status
from ..serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

# ------------------ View para criação de usuario ---------------------
@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        new_user = request.data # recebe os dados do front end
        serializer = UserSerializer(data=new_user) # armazena os dados com o serializer
        serializer.is_valid(raise_exception=True) # valida se os dados estão corretos com o serializer, se estiver errado vai soltar a excessão
        new_user = serializer.save() # salva o usuario no banco de dados
        return Response(serializer.data, {"sucess": True, "message":"Usuário criado com sucesso"}, status=status.HTTP_201_CREATED) # retorna para o front end os dados salvos, uma mensagem de sucesso e o status
    except ValidationError as e:
        return Response({"sucess": False, "message":{e}}, status=status.HTTP_400_BAD_REQUEST) # retorna a excessão
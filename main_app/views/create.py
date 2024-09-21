from rest_framework import status
from ..serializers import UserSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt

# ------------------ View para criação de usuario ---------------------
@csrf_exempt
@api_view(['POST'])
def create_user(request):
    try:
        new_user = request.data
        serializer = UserSerializer(data=new_user)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return JsonResponse({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
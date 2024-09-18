from rest_framework import status
from ..models import User
from rest_framework.response import Response
from ..serializers import UserSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view,  permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

# ------------------ View para deletar um usuario do banco de dados ---------------------     
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    if request.method == 'DELETE':
            try:
                user = User.objects.get(pk=id)
                user = request.user
                if user.is_authenticated:
                    user.delete()
                    return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                JsonResponse({'error': 'User not avaible'})
    

# ------------------ View para atualizar algum dado do cliente ---------------------     
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def user_update(request):
    if request.method == 'PUT':
            try:
                user = User.objects.get(pk=id)
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except ValidationError as e:

                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# ------------------ View para acessar o cadastro do usuario  ---------------------     
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_account(request):
    if request.method == 'GET':
            try:
                user = User.objects.get(pk=id)  # Usa o id recebido na URL
                serializer = UserSerializer(user)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
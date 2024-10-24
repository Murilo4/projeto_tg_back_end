from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import User
from rest_framework import status


@csrf_exempt
@api_view(['GET'])
def cron_job(request):
    return JsonResponse({'message': 'Cron job executed successfully'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
def get_user_to_deck(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'id': user.id,
            'email': user.email,
            'user_name': user.user_name,
            'nick_name': user.nick_name,
            'phone_number': user.phone_number,
            'user_img': user.user_img,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'},
                            status=status.HTTP_404_NOT_FOUND)

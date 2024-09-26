from rest_framework import status
from ..models import User
from ..serializers import DeckSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view,  permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

         
# ------------------ View para criação de deck personalizado ---------------------      
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_deck(request):
    if request == 'POST':
        try:
            deck = request.data
            serializer = DeckSerializer(data=deck)
            serializer.is_valid(raise_exception=True)
            if serializer:
                deck = serializer.save()
        except Exception as e:
            return JsonResponse('error: {e}', status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
    


    



# ------------------ View para visualização de deck personalizado ---------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_deck(request):
    if request.method == 'GET':
            try:
                deck = DeckSerializer.objects.get(pk=id)  # Usa o id recebido na URL
                serializer = DeckSerializer(deck)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Deck not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
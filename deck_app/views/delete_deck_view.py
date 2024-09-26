from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from serializers import DeckSerializer
from rest_framework.decorators import api_view,  permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

# ------------------ View para exclusão de deck personalizado ---------------------
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def create_new_deck(request):
    if request == 'DELETE':
        try:
            deck = DeckSerializer.objects.get(pk=id)
            deck = request.deck
            if deck.is_authenticated:
                deck.delete()
                deck.save()
                return Response({'message': 'Deck deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Deck not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            JsonResponse({'error': 'Deck not avaible'})
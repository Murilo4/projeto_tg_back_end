from django.shortcuts import render
from rest_framework import status
from ..models import User
from ..serializers import DeckSerializer
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view,  permission_classes
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

# ------------------ View para atualização de deck personalizado ---------------------      
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def create_deck(request):
    if request == 'PUT':
        try:
            deck = create_deck.objects.get(pk=id)
            serializer = DeckSerializer(deck, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_202_ACCEPTED)
        except create_deck.DoesNotExist:
            return JsonResponse('error: Deck not found', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse('error: {e}', status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse(status=status.HTTP_400_BAD_REQUEST)
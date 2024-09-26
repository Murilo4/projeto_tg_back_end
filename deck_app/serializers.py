from rest_framework import serializers
from models import Deck

class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model: Deck
        fields = ('user_id', 'id', 'name', 'favorite', 'situation', 'description'
                  , 'new', 'learning', 'review', 'img_url','created_at', 'updated_at')

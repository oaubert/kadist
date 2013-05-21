from rest_framework import serializers
from .models import Work, Artist

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Work
        fields = ('id', 'creator', 'title', 'worktype', 'technique','dimensions', 'description')

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)

    class Meta:
        model = Artist
        fields = ('name', 'country', 'description')

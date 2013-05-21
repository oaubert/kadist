from rest_framework import serializers
from .models import Work, Artist

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    tags = serializers.ManyRelatedField(source='tags')

    class Meta:
        model = Work
        fields = ('id', 'creator', 'title', 'worktype', 'technique','dimensions', 'description', 'tags')

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    works = serializers.HyperlinkedRelatedField(many=True, read_only=True,
                                                view_name='work-detail')
    tags = serializers.ManyRelatedField(source='tags')

    class Meta:
        model = Artist
        fields = ('name', 'country', 'description', 'works', 'tags')

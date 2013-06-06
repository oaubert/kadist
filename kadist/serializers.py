from rest_framework import serializers
from .models import Work, Artist

class ArtistReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for an artist reference.
    """
    class Meta:
        model = Artist
        fields = ('url', 'id', 'name', )

class WorkReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for a work reference.
    """
    artist = ArtistReferenceSerializer(source='creator', read_only=True)
    class Meta:
        model = Work
        fields = ('url', 'id', 'artist', 'title')

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.ManyRelatedField(source='tags')
    similar = WorkReferenceSerializer(source='tags.similar_objects')
    artist = ArtistReferenceSerializer(source='creator')
    class Meta:
        model = Work
        fields = ('url', 'artist', 'title', 'worktype', 'technique','dimensions', 'description', 'tags', 'similar')

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    works = WorkReferenceSerializer(source='works')
    tags = serializers.ManyRelatedField(source='tags')

    class Meta:
        model = Artist
        fields = ('url', 'name', 'country', 'description', 'works', 'tags')

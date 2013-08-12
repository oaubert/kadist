from rest_framework import serializers
from .models import Work, Artist

class ArtistReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for an artist reference.
    """
    kurl = serializers.CharField(source="url")
    class Meta:
        model = Artist
        fields = ('url', 'id', 'name', 'kurl', 'imgurl')

class WorkReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for a work reference.
    """
    artist = ArtistReferenceSerializer(source='creator', read_only=True)
    kurl = serializers.CharField(source="url")
    class Meta:
        model = Work
        fields = ('url', 'id', 'artist', 'title', 'kurl', 'imgurl')

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.RelatedField(source='weighted_tags')
    similar = WorkReferenceSerializer(source='tags.similar_objects')
    artist = ArtistReferenceSerializer(source='creator')
    kurl = serializers.CharField(source="url")
    class Meta:
        model = Work
        fields = ('url', 'id', 'artist', 'title',
                  'worktype', 'technique','dimensions', 'description',
                  'tags', 'similar', 'kurl', 'imgurl')

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    works = WorkReferenceSerializer(source='works')
    tags = serializers.RelatedField(source='weighted_tags')
    kurl = serializers.CharField(source="url")

    class Meta:
        model = Artist
        fields = ('url', 'id', 'name', 'country', 'description', 'works',
                  'tags',
                  'kurl', 'imgurl')

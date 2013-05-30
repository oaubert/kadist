from rest_framework import serializers
from .models import Work, Artist

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.ManyRelatedField(source='tags')

    class Meta:
        model = Work
        fields = ('url', 'creator', 'title', 'worktype', 'technique','dimensions', 'description', 'tags')

class WorkReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for a work reference.
    """
    creatorname = serializers.CharField(source='creator.name', read_only=True)
    class Meta:
        model = Work
        fields = ('url', 'creatorname', 'title')

class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    works = serializers.HyperlinkedRelatedField(many=True, read_only=True,
                                                view_name='work-detail')
    tags = serializers.ManyRelatedField(source='tags')

    class Meta:
        model = Artist
        fields = ('url', 'name', 'country', 'description', 'works', 'tags')

class ArtistReferenceSerializer(serializers.HyperlinkedModelSerializer):
    """Minimal serialization for an artist reference.
    """
    class Meta:
        model = Artist
        fields = ('url', 'name', )

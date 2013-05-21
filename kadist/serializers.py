from rest_framework import serializers
from kadist import models

class WorkSerializer(serializers.HyperlinkedModelSerializer):
    num = serializers.IntegerField(read_only=True)
    creator = serializers.CharField()
    title = serializers.CharField()
    worktype = serializers.CharField()
    technique = serializers.CharField()
    dimensions = serializers.CharField()
    description = serializers.CharField()
    tags = serializers.CharField()

    class Meta:
        model = models.Work
        fields = ('num', 'creator', 'title', 'worktype', 'technique','dimensions', 'description', 'tags')

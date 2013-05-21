from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.db.models.loading import get_model

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Artist, Work
from .serializers import ArtistSerializer, WorkSerializer

# define the default models for tags and tagged items
TAG_MODEL = get_model('taggit', 'Tag')

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'works': reverse('work-list', request=request),
            })

@login_required
def taglist(request):
    keywords = TAG_MODEL.objects.all().values_list('name', flat=True)
    return render_to_response('main.html', {
            'keywords': keywords
            }, context_instance=RequestContext(request))

@login_required
def tag(request, kw=None):
    works = Work.objects.filter(tags__name__in=[kw])
    artists = Artist.objects.filter(tags__name__in=[kw])
    synonyms = []
    return render_to_response('tag.html', {
            'kw': kw,
            'works': works,
            'artists': artists,
            'synonyms': synonyms,
            }, context_instance=RequestContext(request))

class WorkList(generics.ListCreateAPIView):
    model = Work
    serializer_class = WorkSerializer

class WorkDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Work
    serializer_class = WorkSerializer

class ArtistList(generics.ListCreateAPIView):
    model = Artist
    serializer_class = ArtistSerializer

class ArtistDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Artist
    serializer_class = ArtistSerializer

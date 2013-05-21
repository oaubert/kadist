import operator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.db.models.loading import get_model
from django.db.models import Count

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from nltk.corpus import wordnet as wn

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
    tags = TAG_MODEL.objects.annotate(count=Count('taggit_taggeditem_items')).values_list('name', 'count')
    return render_to_response('main.html', {
            'tags': tags
            }, context_instance=RequestContext(request))

@login_required
def tag(request, kw=None):
    works = Work.objects.filter(tags__name__in=[kw])
    artists = Artist.objects.filter(tags__name__in=[kw])

    synsets = wn.synsets(kw)

    synonyms = []
    names = set(n for s in synsets for n in s.lemma_names)
    for n in names:
        c = Work.objects.filter(tags__name__in=[n]).count()
        if c or True:
            synonyms.append( (n, c) )
    synonyms.sort(key=operator.itemgetter(1), reverse=True)

    hypernyms = []
    names = set(h for s in synsets for n in s.hypernyms() for h in n.lemma_names)
    for n in names:
        c = Work.objects.filter(tags__name__in=[n]).count()
        if c or True:
            hypernyms.append( (n, c) )
    hypernyms.sort(key=operator.itemgetter(1), reverse=True)

    hyponyms = []
    names = set(h for s in synsets for n in s.hyponyms() for h in n.lemma_names)
    for n in names:
        c = Work.objects.filter(tags__name__in=[n]).count()
        if c or True:
            hyponyms.append( (n, c) )
    hyponyms.sort(key=operator.itemgetter(1), reverse=True)

    return render_to_response('tag.html', {
            'kw': kw,
            'works': works,
            'artists': artists,
            'synonyms': synonyms,
            'hypernyms': hypernyms,
            'hyponyms': hyponyms,
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

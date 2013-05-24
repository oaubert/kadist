import operator
import itertools

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.db.models.loading import get_model
from django.db.models import Count
from django.views.generic import RedirectView

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from nltk.corpus import wordnet as wn

from .models import Artist, Work
from .serializers import ArtistSerializer, WorkSerializer

# define the default models for tags and tagged items
TAG_MODEL = get_model('taggit', 'Tag')

MIN_RELATED_TAGS_COUNT = 2
DISPLAY_ALL_RELATED_TAGS = False
MAX_SEARCHED_TAGS_COUNT = 200

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'works': reverse('work-list', request=request),
            })

@login_required
def taglist(request):
    kw = request.REQUEST.get('keyword', '')
    if kw:
        # Redirect
        return HttpResponseRedirect('/kadist/tag/%s' % kw)

    tags = TAG_MODEL.objects.annotate(count=Count('taggit_taggeditem_items')).values_list('name', 'count').order_by('name')
    maxcount = max( t[1] for t in tags )
    mincount = 6
    minsize = 10
    maxsize = 48
    factor = 1. * (maxsize - minsize) / (maxcount - mincount)
    def tagsize(c):
        return long(minsize + factor * (c - mincount))
    tags = [ (t[0], t[1], tagsize(t[1]))
             for t in tags
             if t[1] >= mincount ]
    return render_to_response('main.html', {
            'tags': tags
            }, context_instance=RequestContext(request))

# TODO: factorize tag info extraction into struct and use it in tag method + api/tag (JSON version) + angular view

@login_required
def tag(request, kw=None):
    works = Work.objects.filter(tags__name__in=[kw])
    artists = Artist.objects.filter(tags__name__in=[kw])

    if ' ' in kw:
        kwl = kw.split()
        synsets = [ s
                    for k in kwl
                    if k not in ['and', 'or']
                    for s in wn.synsets(k.strip('()"')) 
                    ]
    else:
        synsets = wn.synsets(kw)
    print kw, len(synsets)

    def related_tags(func):
        rel = []
        names = set(n
                    for s in synsets
                    for r in func(s)
                    for n in r.lemma_names)
        if len(names) > MAX_SEARCHED_TAGS_COUNT:
            names = list(names)[:MAX_SEARCHED_TAGS_COUNT]
        for n in names:
            c = Work.objects.filter(tags__name__in=[n]).count()
            if c > MIN_RELATED_TAGS_COUNT or DISPLAY_ALL_RELATED_TAGS:
                rel.append( (n, c) )
        rel.sort(key=operator.itemgetter(1), reverse=True)
        return rel

    synonyms = related_tags(lambda s: [s])
    hypernyms = related_tags(lambda s: itertools.chain(s.hypernyms(), s.instance_hypernyms()))
    hyponyms = related_tags(lambda s: itertools.chain(s.hyponyms(), s.instance_hyponyms()))
    holonyms = related_tags(lambda s: itertools.chain(s.member_holonyms(), s.substance_holonyms(), s.part_holonyms()))
    meronyms = related_tags(lambda s: itertools.chain(s.member_meronyms(), s.substance_meronyms(), s.part_meronyms()))

    return render_to_response('tag.html', {
            'kw': kw,
            'works': works,
            'artists': artists,
            'synonyms': synonyms,
            'hypernyms': hypernyms,
            'hyponyms': hyponyms,
            'holonyms': holonyms,
            'meronyms': meronyms,
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

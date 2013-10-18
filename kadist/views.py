import operator
import itertools

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models.loading import get_model
from django.db.models import Count

from rest_framework import generics
from rest_framework.renderers import UnicodeJSONRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from nltk.corpus import wordnet as wn

from .models import Artist, Work, MajorTag
from .serializers import ArtistSerializer, WorkSerializer, ArtistReferenceSerializer, WorkReferenceSerializer
from .templatetags.kadist import tagsize, TAG_MINCOUNT

# define the default models for tags and tagged items
TAG_MODEL = get_model('taggit', 'Tag')
MAJOR_TAG_MODEL = MajorTag

MIN_RELATED_TAGS_COUNT = 0
DISPLAY_ALL_RELATED_TAGS = False
MAX_SEARCHED_TAGS_COUNT = 200

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'works': reverse('work-list', request=request),
            })

def taglist():
    """Return the decorated list of existing tags.

    The list is decorated with the item count for each tag, and the corresponding tagsize in points.
    """
    tags = TAG_MODEL.objects.annotate(count=Count('taggit_taggeditem_items')).values_list('name', 'count').order_by('name')
    majortags = MajorTag.objects.annotate(count=Count('kadist_majortaggeditem_items')).values_list('name', 'count').order_by('name')
    tags = [ (t[0], t[1], tagsize(t[1]))
             for t in itertools.chain(tags, majortags)
             if t[1] >= TAG_MINCOUNT ]
    return tags

def taginfo(kw):
    """Return information about a tag.

    It returns a dict with the following keys:
            'tag': tag
            'minor_works': list of minor works
            'major_works': list of major works
            'artists': list of artists,
            'synonyms': list of synonyms
            'hypernyms': list of hypernyms
            'hyponyms': list of hyponyms
            'holonyms': list of holonyms
            'meronyms': list of meronyms
    """
    info = { 'tag': kw }

    info['minor_works'] = set(Work.objects.filter(tags__name__in=[kw]))
    info['major_works'] = set(Work.objects.filter(major_tags__name__in=[kw]))
    info['artists'] = Artist.objects.filter(tags__name__in=[kw])

    if ' ' in kw:
        kwl = kw.split()
        synsets = [ s
                    for k in kwl
                    if k not in ['and', 'or']
                    for s in wn.synsets(k.strip('()"'))
                    ]
    else:
        synsets = wn.synsets(kw)

    def related_tags(func):
        rel = []
        names = set(n
                    for s in synsets
                    for r in func(s)
                    for n in r.lemma_names
                    if n != kw)
        if len(names) > MAX_SEARCHED_TAGS_COUNT:
            names = list(names)[:MAX_SEARCHED_TAGS_COUNT]
        for n in names:
            c = Work.objects.filter(tags__name__in=[n]).count()
            if c > MIN_RELATED_TAGS_COUNT or DISPLAY_ALL_RELATED_TAGS:
                rel.append( (n, c) )
            else:
                c = Work.objects.filter(major_tags__name__in=[n]).count()
                if c > MIN_RELATED_TAGS_COUNT or DISPLAY_ALL_RELATED_TAGS:
                    rel.append( (n, c) )
        rel.sort(key=operator.itemgetter(1), reverse=True)
        return rel

    info['synonyms'] = related_tags(lambda s: [s])
    info['hypernyms'] = related_tags(lambda s: itertools.chain(s.hypernyms(), s.instance_hypernyms()))
    info['hyponyms'] = related_tags(lambda s: itertools.chain(s.hyponyms(), s.instance_hyponyms()))
    info['holonyms'] = related_tags(lambda s: itertools.chain(s.member_holonyms(), s.substance_holonyms(), s.part_holonyms()))
    info['meronyms'] = related_tags(lambda s: itertools.chain(s.member_meronyms(), s.substance_meronyms(), s.part_meronyms()))

    return info

@login_required
def taglist_as_html(request):
    kw = request.REQUEST.get('keyword', '')
    if kw:
        # Redirect
        return HttpResponseRedirect('/kadist/tag/%s' % kw)
    else:
        return render_to_response('main.html', {
                'tags': taglist()
                }, context_instance=RequestContext(request))

@api_view(['GET'])
@renderer_classes((UnicodeJSONRenderer, ))
@login_required
def taglist_as_json(request):
    return Response(taglist())

@api_view(['GET'])
@renderer_classes((UnicodeJSONRenderer, ))
@login_required
def tag_as_json(request, kw=None):
    info = taginfo(kw)
    info['minor_works'] = WorkReferenceSerializer(info['minor_works'], many=True, context={'request': request}).data
    info['major_works'] = WorkReferenceSerializer(info['major_works'], many=True, context={'request': request}).data
    info['artists'] = ArtistReferenceSerializer(info['artists'], many=True, context={'request': request}).data
    return Response(info)

@login_required
def tag(request, kw=None):
    return render_to_response('tag.html', taginfo(kw),
                              context_instance=RequestContext(request))

@api_view(['GET'])
@renderer_classes((UnicodeJSONRenderer, ))
@login_required
def complete(request, type=None):
    kw = request.REQUEST.get('term', '')
    if kw:
        res = TAG_MODEL.objects.filter(name__istartswith=kw).annotate(count=Count('taggit_taggeditem_items')).values_list('name', 'count').order_by('-count', 'name')
    else:
        res = [ (kw, 1) ]
    return Response([ { 'value': name, 'label': '%s (%d)' % (name, count) }
                        for (name, count) in res ])

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

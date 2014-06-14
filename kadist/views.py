import operator
import itertools
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models.loading import get_model
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics
from rest_framework.renderers import UnicodeJSONRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from nltk.corpus import wordnet as wn

from .models import Artist, Work, MajorTag, ProfileData, compare, TagSimilarity
from .serializers import ArtistSerializer, WorkSerializer, ArtistReferenceSerializer, WorkReferenceSerializer
from .templatetags.kadist import tagsize, TAG_MINCOUNT

# define the default models for tags and tagged items
TAG_MODEL = get_model('taggit', 'Tag')
MAJOR_TAG_MODEL = MajorTag

MIN_RELATED_TAGS_COUNT = 0
DISPLAY_ALL_RELATED_TAGS = False
MAX_SEARCHED_TAGS_COUNT = 200

SURVEY_WORKS = [
    463,
    548,
    568,
    691,
    709,
    727,
    796,
    820,
    907,
    988,
    ]

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
            'tagsimilar': list of works with a similar (>.8) common tag
            'similar_tags': list of similar (>.8) tags
    """
    info = { 'tag': kw }

    info['minor_works'] = set(Work.objects.filter(tags__name__in=[kw]))
    info['major_works'] = set(Work.objects.filter(major_tags__name__in=[kw]))
    info['artists'] = Artist.objects.filter(tags__name__in=[kw])

    try:
        sim = TagSimilarity.objects.get(ref=kw)
        info['similar_tags'] = sim.similar.split(',')
        info['tagsimilar'] = set(Work.objects.filter(major_tags__name__in=info['similar_tags']))
    except ObjectDoesNotExist:
        info['tagsimilar'] = []
        info['similar_tags'] = []

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

@login_required
def majortaglist_as_html(request):
    worklist = Work.objects.annotate(count=Count('major_tags')).order_by('-count')
    return render_to_response('majortags.html', {
            'object_list': worklist,
            }, context_instance=RequestContext(request))

@login_required
def survey_as_html(request, profile=None):
    works = [ Work.objects.get(pk=i) for i in SURVEY_WORKS ]
    if profile is None or profile == '':
        profiles = ProfileData.objects.order_by('profile').values_list('profile', flat=True)
    else:
        profiles = [ long(profile) ]
    return render_to_response('survey.html', {
            'works': works,
            'profiles': profiles,
            }, context_instance=RequestContext(request))

@login_required
def similaritymatrix_as_html(request, origin, destination):
    origin = Work.objects.get(pk=origin)
    destination = Work.objects.get(pk=destination)
    cols = destination.major_tags.values_list('name', flat=True)
    data = [ (t, [ compare(t, d) for d in destination.major_tags.values_list('name', flat=True) ])
             for t in origin.major_tags.values_list('name', flat=True) ]
    return render_to_response('matrix.html', {
            'origin': origin,
            'destination': destination,
            'cols': cols,
            'data': data,
            }, context_instance=RequestContext(request))

@login_required
def tagsimilarity_as_html(request, tag):
    try:
        sim = TagSimilarity.objects.get(ref=tag)
    except ObjectDoesNotExist:
        return HttpResponse("<h1>No tags with a similarity > 0.8 with %s</h1>" % tag)

    similar = sim.similar.split(',')
    works = set(Work.objects.filter(major_tags__name__in=similar))
    return render_to_response('simtag.html', {
            'tag': tag,
            'similar_tags': similar,
            'object_list': works,
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

MAX_SUGGESTIONS = 20
def suggest(request):
    """
    Returns a list of JSON objects with a `name` and a `value` property that
    all start like your query string `q` (not case sensitive).
    """
    query = request.GET.get('q', '')
    limit = request.GET.get('limit', MAX_SUGGESTIONS)
    try:
        request.GET.get('limit', MAX_SUGGESTIONS)
        limit = min(int(limit), MAX_SUGGESTIONS)  # max or less
    except ValueError:
        limit = MAX_SUGGESTIONS

    data = []
    if '.' in query:
        # Synset
        try:
            # Exact term. Try to propose more specific terms.
            s = wn.synset(query)
            hypo = s.hyponyms()
            if hypo:
                data.append( { 'name': "------------------ More specific term ------------------", 'value': "*More_specific*" })
                data.extend( {'name': '%s - %s' % (n.name, n.definition), 'value': n.name} for n in hypo )
        except:
            # Keep only the 1st part
            query = query.split('.')[0]

    s = wn.synsets(query)
    if s:
        data.append( { 'name':  "------------------ Disambiguation ------------------", 'value': "*Disambiguation*" })
        data.extend( {'name': '%s - %s' % (n.name, n.definition), 'value': n.name} for n in s )

    # Matching existing tags
    tag_name_qs = MajorTag.objects.filter(name__icontains=query).values_list('name', flat=True)
    if tag_name_qs:
        data.append( { 'name': "------------------ Existing tags ------------------", 'value': "*Existing_tags*" })
        data.extend({'name': n, 'value': n} for n in tag_name_qs[:limit])

    return HttpResponse(json.dumps(data), content_type='application/json')

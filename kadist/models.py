from django.db import models
from django.core.urlresolvers import reverse
from taggit_autosuggest.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

from gettext import gettext as _

import nltk
from nltk.corpus import wordnet as wn
from itertools import product

def compare(word1, word2):
    if word1 == word2:
        return 1.0
    ss1 = wn.synsets(word1)
    ss2 = wn.synsets(word2)
    if ss1 and ss2:
        return max(s1.wup_similarity(s2) for (s1, s2) in product(ss1, ss2)) or 0
    else:
        return 0

class MajorTag(TagBase):
    class Meta:
        verbose_name = _("Major Tag")
        verbose_name_plural = _("Major Tags")

class MajorTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey('MajorTag',
                            related_name="%(app_label)s_%(class)s_items")

class Artist(models.Model):
    name = models.CharField("name",
                            max_length=190,
                            unique=False)
    url = models.URLField(verbose_name='Artist URL on the Kadist website',
                          max_length=255,
                          blank=True)
    imgurl = models.URLField(verbose_name='Image URL on the Kadist website',
                          max_length=255,
                          blank=True)
    country = models.CharField("country",
                               max_length=200,
                               blank=True)
    description = models.TextField(_("description"),
                                   blank=True)
    tags = TaggableManager(blank=True)

    @property
    def weighted_tags(self):
        """Return a tuple list with the weight for each tag.
        """
        # The aggregation API should work here, but seems not to.
        # return self.tags.annotate(count=models.Count('taggit_taggeditem_items')).values_list('name', 'count').order_by('name')
        return [ (t.name, t.taggit_taggeditem_items.count()) for t in self.tags.all() ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('artist-detail', args=[str(self.pk)])

class Work(models.Model):
    creator = models.ForeignKey(Artist,
                                verbose_name="artist",
                                related_name='works')
    url = models.URLField(verbose_name='Work URL on the Kadist website',
                          max_length=255,
                          blank=True)
    imgurl = models.URLField(verbose_name='Image URL on the Kadist website',
                          max_length=255,
                          blank=True)
    title = models.CharField(_("title"),
                             max_length=255,
                             blank=True)
    year = models.IntegerField("created",
                               null=True)
    worktype = models.CharField(_("work type"),
                                max_length=255,
                                blank=True)
    technique = models.CharField(_("technique"),
                                 max_length=255,
                                 blank=True)
    dimensions = models.CharField(_("dimensions"),
                                    max_length=255,
                                    blank=True)
    description = models.TextField(_("description"),
                                   blank=True)

    major_tags = TaggableManager(verbose_name='Major tags', blank=True, through=MajorTaggedItem)
    tags = TaggableManager(verbose_name='Minor tags', blank=True)

    @property
    def weighted_tags(self):
        """Return a tuple list with the weight for each tag.
        """
        return [ (t.name, t.taggit_taggeditem_items.count()) for t in self.tags.all() ]

    @property
    def weighted_major_tags(self):
        """Return a tuple list with the weight for each major tag.
        """
        return [ (t.name, t.kadist_majortaggeditem_items.count()) for t in self.major_tags.all() ]

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.creator)

    def get_absolute_url(self):
        return reverse('work-detail', args=[str(self.pk)])

    def similarity(self, work, MAXITEMS=5, MAJMIN=.5, MINMAJ=.5):
        s = 0
        if self.major_tags.all() and work.major_tags.all():
            s = len(list(t
                         for t in product(self.major_tags.values_list('name', flat=True),
                                          work.major_tags.values_list('name', flat=True))
                         if (compare(t[0], t[1]) > .8)))
        return s

    def similarity2(self, work, MAXITEMS=5, MAJMIN=.5, MINMAJ=.5):
        if self.major_tags.all() and work.major_tags.all():
            majmaj = sum(sorted(filter(lambda x: x,
                                       (compare(t[0], t[1])
                                        for t in product(self.major_tags.values_list('name', flat=True),
                                                         work.major_tags.values_list('name', flat=True)))),
                                reverse=True)[:MAXITEMS])
        else:
            majmaj = 0

        if self.tags.all() and work.major_tags.all():
            majmin = sum(sorted(filter(lambda x: x,
                                       (compare(t[0], t[1])
                                        for t in product(self.major_tags.values_list('name', flat=True),
                                                         work.tags.values_list('name', flat=True)))),
                                reverse=True)[:MAXITEMS])
        else:
            majmin = 0

        if self.major_tags.all() and work.tags.all():
            minmaj = sum(sorted(filter(lambda x: x,
                                       (compare(t[0], t[1]) for t in product(self.tags.values_list('name', flat=True),
                                                                             work.major_tags.values_list('name', flat=True)))),
                                reverse=True)[:MAXITEMS])
        else:
            minmaj = 0

        return (majmaj + MAJMIN * majmin + MINMAJ * minmaj) / (MAXITEMS * (1 + MINMAJ + MAJMIN))

    def similarity1(self, work, MAXITEMS=5, MAJMIN=.5, MINMAJ=.5):
        if self.major_tags.all() and work.major_tags.all():
            majmaj = sum(sorted( ( max(compare(target, other) for other in work.major_tags.values_list('name', flat=True))
                                   for target in self.major_tags.values_list('name', flat=True) ),
                                 reverse=True)[:MAXITEMS])
        else:
            majmaj = 0

        if self.tags.all() and work.major_tags.all():
            majmin = sum(sorted( ( max(compare(target, other) for other in work.major_tags.values_list('name', flat=True))
                                   for target in self.tags.values_list('name', flat=True) ),
                                 reverse=True)[:MAXITEMS])
        else:
            majmin = 0

        if self.major_tags.all() and work.tags.all():
            minmaj = sum(sorted( ( max(compare(target, other) for other in work.tags.values_list('name', flat=True))
                                   for target in self.major_tags.values_list('name', flat=True) ),
                                 reverse=True)[:MAXITEMS])
        else:
            minmaj = 0

        return (majmaj + MAJMIN * majmin + MINMAJ * minmaj) / (MAXITEMS * (1 + MINMAJ + MAJMIN))

    def similar(self, profile=None):
        """Return the list of similar works for the given profile.
        """
        if profile is None:
            # Not optimal, since it will compute all lists. But the
            # amount of data is negligible compared to the time to
            # debug this properly.  
            # TODO: implement better later, through functional.partial or django curry
            return [ { 'profile': p.profile,
                       'info': p,
                       'works': self.similar(p.profile) }
                     for p in ProfileData.objects.all() ]
        else:
            return [ { 'work': s.destination,
                       'similarity': s.value }
                     for s in SimilarityMatrix.objects.filter(profile=profile, origin=self).order_by('-value')[:10] ]

class SimilarityMatrix(models.Model):
    origin = models.ForeignKey(Work, related_name="similarity_origin")
    destination = models.ForeignKey(Work, related_name="similarity_destination")
    profile = models.IntegerField()
    value = models.FloatField()
    
    def __unicode__(self):
        return "(%d - %d)[%d] = %.02f" % (self.origin.pk, self.destination.pk, self.profile, self.value)

class ProfileData(models.Model):
    profile = models.IntegerField(unique=True)
    name = models.CharField("name",
                            max_length=127,
                            unique=False)
    maxitems = models.IntegerField()
    minmaj = models.FloatField()
    majmin = models.FloatField()

    def __unicode__(self):
        return "Profile %s [%d]: maxitems = %d - min/maj = %.02f - maj/min = %.02f" % (self.name, self.profile, self.maxitems, self.minmaj, self.majmin)


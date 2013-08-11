from django.db import models
from django.core.urlresolvers import reverse
from taggit_autosuggest.managers import TaggableManager

from gettext import gettext as _

class Artist(models.Model):
    name = models.CharField("name",
                            max_length=190,
                            unique=False)
    url = models.URLField(verbose_name='Artist URL on the Kadist website',
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
    tags = TaggableManager(blank=True)

    @property
    def weighted_tags(self):
        """Return a tuple list with the weight for each tag.
        """
        return [ (t.name, t.taggit_taggeditem_items.count()) for t in self.tags.all() ]

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.creator)

    def get_absolute_url(self):
        return reverse('work-detail', args=[str(self.pk)])

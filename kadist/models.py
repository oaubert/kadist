from django.db import models

from taggit_autosuggest.managers import TaggableManager

from gettext import gettext as _

class Artist(models.Model):
    name = models.CharField("name",
                            max_length=200,
                            unique=True)
    url = models.URLField(verbose_name='Artist URL on the Kadist website',
                          max_length=255,
                          blank=True)
    country = models.CharField("country",
                               max_length=200,
                               blank=True)
    description = models.TextField(_("description"),
                                   blank=True)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.name

# Create your models here.
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
    # tags
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.creator)


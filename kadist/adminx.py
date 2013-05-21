import xadmin
from xadmin import views
#from xadmin.layout import *

from xadmin.plugins.batch import BatchChangeAction

from .models import Artist, Work

class MainDashboard(object):
    widgets = [
        ]
xadmin.site.register(views.website.IndexView, MainDashboard)

class BaseSetting(object):
    enable_themes = False
    use_bootswatch = True
xadmin.site.register(views.BaseAdminView, BaseSetting)

class WorkAdmin(object):
    list_display = ('title', 'worktype', 'year', 'creator', 'technique', 'description', 'the_tags')
    list_display_links = ('title',)
    list_filter = ( 'creator', 'title' )
    search_fields = [ 'creator', 'title', 'description', 'the_tags' ]
    #relfield_style = 'fk-ajax'
    reversion_enable = False

    actions = [ BatchChangeAction, ]
    batch_fields = ('worktype', )
    
    def the_tags(self, obj):
        return ", ".join(unicode(t.name) for t in obj.tags.all())

xadmin.site.register(Work, WorkAdmin)

class ArtistAdmin(object):
    list_display = ('name', 'country', 'description', 'the_tags' )
    list_display_links = ('name',)
    list_filter = ( 'country', )
    search_fields = [ 'name', 'country', 'description', 'the_tags' ]
    #relfield_style = 'fk-ajax'
    reversion_enable = False

    def the_tags(self, obj):
        return ", ".join(unicode(t.name) for t in obj.tags.all())

xadmin.site.register(Artist, ArtistAdmin)

from django.contrib import admin
from .models import Artist, Work

class WorkAdmin(admin.ModelAdmin):
    fields = ('title', 'tags', 'worktype', 'year', 'creator', 'technique', 'url', 'description')
    list_display = ('title', 'tags_as_string', 'worktype', 'year', 'creator', 'technique', 'description')
    list_display_links = ('title',)
    list_filter = ( 'creator', 'worktype', 'year' )
    search_fields = [ 'creator', 'title', 'description' ]
    def tags_as_string(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    tags_as_string.short_description = 'Tags'
admin.site.register(Work, WorkAdmin)

class ArtistAdmin(admin.ModelAdmin):
    fields = ('name', 'tags', 'country', 'url', 'description' )
    list_display = ('name', 'tags_as_string', 'country', 'description' )
    list_display_links = ('name',)
    list_filter = ( 'country', )
    search_fields = [ 'name', 'country', 'description' ]
    def tags_as_string(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    tags_as_string.short_description = 'Tags'
admin.site.register(Artist, ArtistAdmin)


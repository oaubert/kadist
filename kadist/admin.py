from django.contrib import admin
from .models import Artist, Work

class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'worktype', 'year', 'creator', 'technique', 'description', 'tags')
    list_display_links = ('title',)
    list_filter = ( 'creator', 'worktype', 'year' )
    search_fields = [ 'creator', 'title', 'description' ]
admin.site.register(Work, WorkAdmin)

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'description', 'tags' )
    list_display_links = ('name',)
    list_filter = ( 'country', )
    search_fields = [ 'name', 'country', 'description' ]

admin.site.register(Artist, ArtistAdmin)


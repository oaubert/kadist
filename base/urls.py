from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^kadist/', include('kadist.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^grappelli/', include('grappelli.urls')),
                       url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
)

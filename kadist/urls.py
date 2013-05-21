from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib import admin
from kadist import views

urlpatterns = patterns('',
                       url(r'^work/$', views.WorkList.as_view(), name='work-list'),
                       url(r'^work/(?P<pk>[0-9]+)/$', views.WorkDetail.as_view(), name='work-detail'), 
                       url(r'^artist/$', views.ArtistList.as_view(), name='artist-list'),
                       url(r'^artist/(?P<pk>[0-9]+)/$', views.ArtistDetail.as_view(), name='artist-detail'), 
                       )

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls',
                                                   namespace='rest_framework')),
                        url(r'^$', views.api_root),
                        )


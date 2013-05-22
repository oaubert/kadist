from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView
from kadist import views
from .models import Work, Artist

urlpatterns = patterns('',
                       url(r'^$', login_required(TemplateView.as_view(template_name='root.html')), name='root'),
                       url(r'^tag/$', views.taglist, name='tag-list'),
                       url(r'^tag/(?P<kw>.+)$', views.tag, name='tag-detail'),
                       url(r'^work/$', login_required(ListView.as_view(model=Work)), name='work-list'),
                       url(r'^work/(?P<pk>[0-9]+)/$', login_required(DetailView.as_view(model=Work, context_object_name='work')),
                           name='work-detail'),
                       url(r'^artist/$', login_required(ListView.as_view(model=Artist)), name='artist-list'),
                       url(r'^artist/(?P<pk>.+)/$', login_required(DetailView.as_view(model=Artist, context_object_name='artist')),
                           name='artist-detail'),

                       # REST API
                       url(r'^api/work/$', views.WorkList.as_view(), name='api-work-list'),
                       url(r'^api/work/(?P<pk>[0-9]+)/$', views.WorkDetail.as_view(), name='api-work-detail'),
                       url(r'^api/artist/$', views.ArtistList.as_view(), name='api-artist-list'),
                       url(r'^api/artist/(?P<pk>[0-9]+)/$', views.ArtistDetail.as_view(), name='api-artist-detail'),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls',
                                                   namespace='rest_framework')),
                        )


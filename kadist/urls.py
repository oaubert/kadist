from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from kadist import views
from .models import Work, Artist

urlpatterns = patterns('',
                       url(r'^$', views.site_root, name='root'),
                       url(r'^tag/$', views.taglist_as_html, name='tag-list'),
                       url(r'^tag/(?P<tag>.+)/similar$', views.tagsimilarity_as_html, name='tag-similarity'),
                       url(r'^tag/(?P<kw>.+)$', views.tag, name='tag-detail'),
                       url(r'^graph/', include(patterns('',
                                                        url(r'^$', RedirectView.as_view(url="tag/")),
                                                        url(r'^(?P<type>tag)/(?P<kw>.*)$',
                                                            login_required(TemplateView.as_view(template_name='graph.html')),
                                                            name='tag-graph'),
                                                        url(r'^(?P<type>work)/(?P<kw>.*)$',
                                                            login_required(TemplateView.as_view(template_name='graph.html')),
                                                            name='work-graph'),
                                                        url(r'^(?P<type>artist)/(?P<kw>.*)$',
                                                            login_required(TemplateView.as_view(template_name='graph.html')),
                                                            name='artist-graph'),
                                                        ))),
                       url(r'^work/$', login_required(ListView.as_view(model=Work)), name='work-list'),
                       url(r'^work/(?P<pk>[0-9]+)/$', login_required(DetailView.as_view(model=Work, context_object_name='work')),
                           name='work-detail'),
                       url(r'^sortedtag/$', views.sortedtaglist_as_html, name='sorted-tag-list'),
                       url(r'^sortedwork/$', views.majortaglist_as_html, name='work-major-list'),
                       url(r'^survey/(?P<profiles>[,0-9]*)$', views.survey_as_html, name='survey'),
                       url(r'matrix/(?P<origin>[0-9]+)/(?P<destination>[0-9]+)$', views.similaritymatrix_as_html, name='matrix'),
                       url(r'^artist/$', login_required(ListView.as_view(model=Artist)), name='artist-list'),
                       url(r'^artist/(?P<pk>.+)/$', login_required(DetailView.as_view(model=Artist, context_object_name='artist')),
                           name='artist-detail'),

                       # REST API
                       url(r'^api/', include(patterns('',
                                                      url(r'^work/$', 
                                                          views.WorkList.as_view(), 
                                                          name='api-work-list'),
                                                      url(r'^work/(?P<pk>[0-9]+)/$', 
                                                          views.WorkDetail.as_view(), 
                                                          name='api-work-detail'),
                                                      url(r'^artist/$', 
                                                          views.ArtistList.as_view(), 
                                                          name='api-artist-list'),
                                                      url(r'^artist/(?P<pk>[0-9]+)/$', 
                                                          views.ArtistDetail.as_view(), 
                                                          name='api-artist-detail'),
                                                      url(r'^tag/$', 
                                                          views.taglist_as_json, 
                                                          name='api-tag-list'),
                                                      url(r'^tag/(?P<kw>.+)$', 
                                                          views.tag_as_json, 
                                                          name='api-tag-detail'),
                                                      )))
                       )

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += patterns('',
                        url(r'^api-auth/', include('rest_framework.urls',
                                                   namespace='rest_framework')),
                        url(r'^complete/(?P<type>tag)$', views.complete, name='complete'),
                        url(r'^suggest/$', views.suggest, name='taggit_autosuggest-list'),
                        )


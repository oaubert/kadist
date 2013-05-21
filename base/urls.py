from django.conf.urls import patterns, include, url
import xadmin
xadmin.autodiscover()
#from xadmin.plugins import xversion
#xversion.register_models()

urlpatterns = patterns('',
                       url(r'^kadist/', include('kadist.urls')),
                       url(r'^admin/', include(xadmin.site.urls)),
)

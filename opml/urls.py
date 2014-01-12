from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'feed.views.index', name='index'),
    url(r'^(?P<slug>.+)\.opml$', 'feed.views.collection_opml', name='collection_opml'),
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'feed.views.index', name='index'),
    url(r'^add/(?P<slug>.+)/$', 'feed.views.edit_collection', name='edit_collection'),
    url(r'^(?P<slug>.+)\.opml$', 'feed.views.view_collection', name='view_collection'),
    url(r'^admin/', include(admin.site.urls)),
)

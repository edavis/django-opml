import requests
import feedparser
from django.contrib import admin
from feed.models import Feed, Collection

class CollectionAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    exclude = ('owner',)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        obj.save()


class FeedAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.update_info()
        obj.save()


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Feed, FeedAdmin)


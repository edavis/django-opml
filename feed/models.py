import requests
import feedparser

from django.db import models
from django.contrib.auth.models import User


class Collection(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.CharField(max_length=200, blank=True)
    private = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, related_name='collections')

    def __unicode__(self):
        return self.title


class Feed(models.Model):
    url = models.URLField('Feed URL', max_length=500)
    title = models.CharField(max_length=100, blank=True)

    html_url = models.URLField('Web URL', max_length=500, blank=True)
    feed_title = models.CharField(max_length=100, blank=True)
    feed_description = models.CharField(max_length=200, blank=True)
    feed_language = models.CharField(max_length=50, blank=True)

    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    collections = models.ManyToManyField(Collection, related_name='feeds')

    def parse_feed(self):
        response = requests.get(self.url, timeout=10, verify=False)
        return feedparser.parse(response.content)

    def update_info(self):
        parsed = self.parse_feed()
        if not self.title:
            self.title = parsed.feed.get('title', '')
        if not self.feed_title:
            self.feed_title = parsed.feed.get('title', '')
        if not self.html_url:
            self.html_url = parsed.feed.get('link', '')
        if not self.feed_description:
            self.feed_description = parsed.feed.get('description', '')
        if not self.feed_language:
            self.feed_language = parsed.feed.get('language', '')
        self.save()

    def __unicode__(self):
        return self.title

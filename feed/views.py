import calendar
from email.utils import formatdate

from lxml import etree
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Max, Min
from django.core.urlresolvers import reverse

from feed.models import Collection, Feed


def format_timestamp(dt):
    """
    Return an RFC 822 timestamp from a UTC, timestamp-aware datetime.
    """
    epoch = calendar.timegm(dt.utctimetuple())
    return formatdate(epoch, usegmt=True)


def add_element(parent, element, text):
    etree.SubElement(parent, element).text = text


def add_collection(parent, collection):
    attrs = {
        'created': format_timestamp(collection.added),
        'name': collection.slug,
        'text': collection.title,
    }
    if collection.description:
        attrs['description'] = collection.description
    return etree.SubElement(parent, 'outline', **attrs)


def add_feed(parent, feed):
    attrs = {
        'created': format_timestamp(feed.added),
        'description': feed.feed_description,
        'htmlUrl': feed.html_url,
        'language': feed.feed_language,
        'text': feed.title,
        'title': feed.feed_title,
        'type': 'rss',
        'xmlUrl': feed.url,
    }
    return etree.SubElement(parent, 'outline', **attrs)


def render_opml(opml):
    serialized = etree.tostring(opml, xml_declaration=True, pretty_print=True, encoding='UTF-8')
    return HttpResponse(serialized, content_type='text/xml')


def build_head(opml):
    head = etree.SubElement(opml, 'head')
    add_element(head, 'ownerName', 'Eric Davis')
    add_element(head, 'ownerEmail', 'eric@davising.com')
    add_element(head, 'ownerId', 'https://twitter.com/ejd791')
    add_element(head, 'docs', 'https://github.com/edavis/django-opml')
    return head


def add_timestamp_headers(qs, head):
    if not qs.exists():
        return
    info = qs.aggregate(dateCreated=Min('added'), dateModified=Max('modified'))
    add_element(head, 'dateCreated', format_timestamp(info['dateCreated']))
    add_element(head, 'dateModified', format_timestamp(info['dateModified']))


def index(request):
    opml = etree.Element('opml', version='2.0')

    head = build_head(opml)
    add_timestamp_headers(Feed.objects.all(), head)

    body = etree.SubElement(opml, 'body')
    for collection in Collection.objects.filter(private=False):
        collection_outline = add_collection(body, collection)
        for feed in collection.feeds.iterator():
            add_feed(collection_outline, feed)

    return render_opml(opml)


def collection_opml(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    opml = etree.Element('opml', version='2.0')

    head = build_head(opml)
    if collection.description:
        add_element(head, 'description', collection.description)
    add_timestamp_headers(collection.feeds.all(), head)

    body = etree.SubElement(opml, 'body')
    for feed in collection.feeds.iterator():
        add_feed(body, feed)

    return render_opml(opml)


def edit_collection(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    if request.method == 'POST':
        feeds = request.POST.get('feeds')
        if not feeds:
            url = reverse('edit_collection', kwargs={'slug': collection.slug})
            return redirect(url)
        for feed_url in feeds.splitlines():
            feed_obj = Feed()
            feed_obj.url = feed_url
            feed_obj.save()
            feed_obj.collections.add(collection)
            feed_obj.save()
            feed_obj.update_info()
        redirect_url = reverse('collection_opml', kwargs={'slug': collection.slug})
        return redirect(redirect_url)
    elif request.method == 'GET':
        return render(request, 'feed/edit_collection.html')

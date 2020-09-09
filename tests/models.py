from django.db import models

from curation.models import CuratedGroup, CuratedItem
from curation.fields import (
    CuratedForeignKey,
    ContentTypeSourceField,
    CuratedGenericForeignKey,
)


class Post(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return '[Post({})]'.format(self.id)


class CuratedPostGroup(CuratedGroup):
    pass


class CuratedPostItem(CuratedItem):
    post = CuratedForeignKey(Post, on_delete=models.CASCADE)
    group = models.ForeignKey(CuratedPostGroup, on_delete=models.CASCADE)

    class Meta:
        ordering = ['position']


class ModelA(models.Model):
    a_field = models.CharField(max_length=20)


class ModelB(models.Model):
    b_field = models.CharField(max_length=20)


class Handler(CuratedItem):
    CONTENT_TYPES = (
        ('tests.Post', 'Post', 'post'),
        (ModelA, 'Model A', 'moda'),
        ('ModelB', 'Model B', 'modb'),
        ('self.url', 'URL', 'url'),
    )

    content_type = ContentTypeSourceField(
        ct_choices=CONTENT_TYPES,
        source_field='source',
        null=True, blank=True)
    object_id = models.PositiveIntegerField()
    content_object = CuratedGenericForeignKey('content_type', 'object_id')
    source = models.CharField(max_length=8, null=True, blank=True)

    field_overrides = {
        'title': 'custom_title',
    }

    custom_title = models.CharField(max_length=50, blank=True)
    url = models.URLField(null=True, blank=True, max_length=500)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        try:
            _id = getattr(self, 'id', 'Unknown')
        except AttributeError:
            _id = 'Unknown'
        return 'Handler({})'.format(_id)

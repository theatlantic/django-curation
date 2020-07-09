from django.db import models

from curation.models import CuratedGroup, CuratedItem
from curation.fields import CuratedForeignKey


class Post(models.Model):
    title = models.CharField(max_length=50)


class CuratedPostGroup(CuratedGroup):
    pass


class CuratedPostItem(CuratedItem):
    post = CuratedForeignKey(Post, on_delete=models.CASCADE)
    group = models.ForeignKey(CuratedPostGroup, on_delete=models.CASCADE)

    class Meta:
        ordering = ['position']

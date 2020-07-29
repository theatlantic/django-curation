import pytest

import curation.views  # noqa
import curation.models  # noqa
import curation.fields  # noqa
import curation.widgets  # noqa
import curation.urls  # noqa

from tests import models


@pytest.mark.django_db
def test_simple_models():
    post = models.Post.objects.create(title='Hello, curation')
    group = models.CuratedPostGroup.objects.create(name='Curated Post Group Name', slug='slug')
    models.CuratedPostItem.objects.create(post=post, group=group, position=1)
    assert models.Post.objects.filter(pk=post.pk, curatedpostitem__group__slug='slug').count()


@pytest.mark.django_db
def test_curated_gfk():
    post = models.Post.objects.create(title='Hello, curation')
    models.Handler.objects.create(content_object=post)

    h = models.Handler.objects.get()
    assert h.content_object.title == 'Hello, curation'

import pytest

import curation.views  # noqa
import curation.models  # noqa
import curation.fields  # noqa
import curation.widgets  # noqa
import curation.urls  # noqa

from tests.models import Post, CuratedPostItem, CuratedPostGroup


@pytest.mark.django_db
def test_models():
    post = Post.objects.create(title='Hello, curation')
    group = CuratedPostGroup.objects.create(name='Curated Post Group Name', slug='slug')
    curated_post = CuratedPostItem.objects.create(post=post, group=group, position=1)
    assert Post.objects.filter(pk=post.pk, curatedpostitem__group__slug='slug').count()

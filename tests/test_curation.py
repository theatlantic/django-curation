import pytest
from pytest_django.asserts import assertHTMLEqual

from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

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


@pytest.mark.django_db
def test_formfield_render():
    post = models.Post.objects.create(title='Hello, curation')
    models.ModelA.objects.create(a_field='a')
    models.ModelB.objects.create(b_field='b')

    handler = models.Handler.objects.create(content_object=post, position=0)

    Form = modelform_factory(models.Handler, exclude=[])
    form = Form(instance=handler)

    assertHTMLEqual(str(form['content_type']), """
    <select name="content_type"
            class="curated-content-type-select"
            data-field-name="content_type"
            data-ct-field-name="content_type"
            data-content-type-id="{ct[handler]}"
            data-fk-field-name="object_id"
            id="id_content_type">
      <option value="">---------</option>
      <option value="{ct[post]}" selected class="curated-content-type-option">Post</option>
      <option value="{ct[a]}" class="curated-content-type-option">Model A</option>
      <option value="{ct[b]}" class="curated-content-type-option">Model B</option>
    </select>""".format(ct={
        "post": ContentType.objects.get_for_model(models.Post).pk,
        "a": ContentType.objects.get_for_model(models.ModelA).pk,
        "b": ContentType.objects.get_for_model(models.ModelB).pk,
        "handler": ContentType.objects.get_for_model(models.Handler).pk,
    }))

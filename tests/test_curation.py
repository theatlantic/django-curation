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
    models.Handler.objects.create(content_object=post, position=0)

    h = models.Handler.objects.get()
    assert h.content_object.title == 'Hello, curation'
    assert h.title == 'Hello, curation'
    assert h.source == 'post'


@pytest.mark.django_db
def test_source_field_descriptor():
    post = models.Post.objects.create(title='Hello, curation')
    a_obj = models.ModelA.objects.create(a_field='a')
    handler = models.Handler.objects.create(content_object=a_obj, position=0)

    handler.source = 'moda'
    assert handler.content_type == ContentType.objects.get_for_model(a_obj)
    handler.object_id = a_obj.pk
    assert handler.content_object == a_obj


@pytest.mark.django_db
def test_curated_gfk_formfield_override():
    post = models.Post.objects.create(title='Hello, curation')
    models.Handler.objects.create(
        content_object=post,
        position=0,
        custom_title='Hello! Curation!')

    h = models.Handler.objects.get()
    assert h.content_object.title == 'Hello, curation'
    assert h.title == 'Hello! Curation!'


@pytest.mark.django_db
def test_contenttype_formfield_render():
    post = models.Post.objects.create(title='Hello, curation')
    models.ModelA.objects.create(a_field='a')
    models.ModelB.objects.create(b_field='b')

    handler = models.Handler.objects.create(content_object=post, position=0)

    Form = modelform_factory(models.Handler, exclude=['source'])
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
      <option class="curated-content-type-option curated-content-type-ptr"
              data-field-name="url" value="{ct[handler]}">URL</option>
    </select>""".format(ct={
        "post": ContentType.objects.get_for_model(models.Post).pk,
        "a": ContentType.objects.get_for_model(models.ModelA).pk,
        "b": ContentType.objects.get_for_model(models.ModelB).pk,
        "handler": ContentType.objects.get_for_model(models.Handler).pk,
    }))


@pytest.mark.django_db
def test_form_save():
    post = models.Post.objects.create(title='Hello, curation')
    a_obj = models.ModelA.objects.create(a_field='a')
    models.ModelB.objects.create(b_field='b')

    handler = models.Handler.objects.create(content_object=post, position=0)

    Form = modelform_factory(models.Handler, exclude=['source'])
    form = Form(instance=handler, data={
        'content_type': str(ContentType.objects.get_for_model(a_obj).pk),
        'object_id': str(a_obj.pk),
        'position': '0',
    })
    handler = form.save()
    assert handler.content_object == a_obj
    assert handler.source == 'moda'

@pytest.mark.django_db
def test_form_save_self_ctype():
    post = models.Post.objects.create(title='Hello, curation')
    a_obj = models.ModelA.objects.create(a_field='a')
    models.ModelB.objects.create(b_field='b')

    handler = models.Handler.objects.create(content_object=post, position=0)

    Form = modelform_factory(models.Handler, exclude=['source'])
    form = Form(instance=handler, data={
        'content_type': str(ContentType.objects.get_for_model(handler).pk),
        'object_id': str(handler.pk),
        'url': 'https://www.theatlantic.com/',
        'custom_title': 'The Atlantic',
        'position': '0',
    })
    handler = form.save()
    assert handler.source == 'url'
    assert handler.title == 'The Atlantic'
    assert handler.url == 'https://www.theatlantic.com/'

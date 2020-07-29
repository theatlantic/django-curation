===============
django-curation
===============

.. image:: https://travis-ci.org/theatlantic/django-curation.svg?branch=master
    :target: https://travis-ci.org/theatlantic/django-curation

**django-curation** is a django module that provides a model used for
curating other model objects and proxying their attributes.

.. note::

    Version(s) < 2.0 requires Django >= 1.11, < 2.0.

    Version(s) >= 2.0 require Python 3, Django >= 2.0.

Example
=======

.. code:: python

    from django.db import models

    from curation.models import CuratedItem, CuratedGroup, CuratedItemManager
    from curation.fields import CuratedForeignKey

    from blog.models import Post

    class CuratedPostGroup(CuratedGroup):
        pass

    class CuratedPost(CuratedItem):
        formfield_overrides = {
            'custom_title': 'title',
        }
        objects = CuratedItemManager()

        group = models.ForeignKey(CuratedPostGroup, on_delete=models.CASCADE)
        post = curation.fields.CuratedForeignKey(Post)
        custom_title = models.CharField(max_length=255, null=True, blank=True,
            db_column='title')

Testing
=======

``tox``
-------

Setup::

    python3 -m venv venv
    . venv/bin/activate
    pip install tox

Run all tests::

    tox

Run code coverage and render HTML report::

    tox -e cov
    open htmlcov/index.html

``pytest``
----------

Setup::

    python3 -m venv venv
    . venv/bin/activate
    pip install pytest pytest-cov pytest-django "Django<2.1"
    pip install -e .

Run tests::

    python -m pytest

Run code coverage and render HTML report::

    python -m pytest --cov-report html --cov-report term --cov=curation

Internals
=========

``curation.models.CuratedItem``
-------------------------------

Abstract class representing an item in a curated group.

In order for a model that extends this class to proxy successfully,
it must define a ``CuratedForeignKey`` field::

    class CuratedPost(CuratedItem):
        post = curation.fields.CuratedForeignKey(Post)

``field_overrides = {}``
------------------------

A dict that maps field names in the proxy model (the to=... model in the
``CuratedForeignKey``) to field names in the current model which can override
them (provided their value is not None or an empty string).

This takes the form::

    field_overrides = {
         'title': 'custom_title',
         'status': 'custom_status',
    }

Where ``custom_title`` and ``custom_status`` are fields in the model extending
``CuratedItem``, and ``title`` and ``status`` are fields in the proxy model.

``primary_id = models.AutoField(primary_key=True, db_column='id')``
-------------------------------------------------------------------

Custom primary key to prevent conflicts with the proxy model's primary key.


``curation.models.CuratedItemManager``
--------------------------------------

A manager that defines queryset helpers for CuratedItem.

``group(<slug>)``
~~~~~~~~~~~~~~~~~

Filter the current queryset to rows with curated groups having slug "slug".


``curation.base.CuratedItemModelBase``
--------------------------------------

Overrides ``ModelBase`` to check whether a ``curation.fields.CuratedForeignKey``
is defined on the model. If not, throw a ``TypeError``.


``curation.fields.CuratedForeignKey``
-------------------------------------

A ForeignKey that gets a list of the ``__dict__`` keys and field names of the
related model on load. It saves this list to the ``_proxy_attrs`` attribute of
its parent model's ``_meta`` attribute.

``contribute_to_class(<cls>, <name>)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A django built-in that adds attributes to the model class in which it is
defined.

This method sets the ``_curated_proxy_field_name`` on the ``_meta`` attribute of the
``CuratedForeignKey``'s parent model to the field's name (e.g. "post" in the example at the very
beginning of this README).

``contribute_to_related_class(<cls>, <related>)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A django built-in that adds attributes to the class a ``RelatedField`` points to.

In this case we're adding ``_proxy_attrs`` to the _meta attribute of the ``ForeignKey``'s parent
model, not the related model. The reason we're not using ``contribute_to_class`` is that we need the
related class to be instantiated to obtain its field names, and the related class may not be loaded
yet when ``contribute_to_class`` is called (for instance, if it is lazy loaded, when the
``ForeignKey`` field is defined using a string for the model).

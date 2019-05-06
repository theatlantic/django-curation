===============
django-curation
===============

**django-curation** is a django module that provides a model used for
curating other model objects and proxying their attributes.

**Note** Version(s) >= 1.3 require Django >= 1.11. Version(s) >= 1.4 require Python 3.

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

Documentation
=============

For more detailed documentation, view the `README <https://github.com/theatlantic/django-curation#django-curation>`_.

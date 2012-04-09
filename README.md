# django-curation

**django-curation** is a django module that provides a model used for curating
other model objects and proxying their attributes.

## Example

```python
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

    group = models.ForeignKey(CuratedPostGroup)
    post = curation.fields.CuratedForeignKey(Post)
    custom_title = models.CharField(max_length=255, null=True, blank=True,
        db_column='title')
```

## Internals

### *class* **curation.models.CuratedItem**

Abstract class representing an item in a curated group.

In order for a model that extends this class to proxy successfully,
it must define a **CuratedForeignKey** field.

```python
class CuratedPost(CuratedItem):
    post = curation.fields.CuratedForeignKey(Post)
```

##### field_overrides = *{}*

A dict that maps field names in the proxy model (the to=... model in the
**CuratedForeignKey**) to field names in the current model which can override
them (provided their value is not None or an empty string).

This takes the form:

```python
field_overrides = {
     'title': 'custom_title',
     'status': 'custom_status',
}
```

Where `custom_title` and `custom_status` are fields in the model extending
**CuratedItem**, and `title` and `status` are fields in the proxy model.

##### primary_id = *models.AutoField(primary_key=True, db_column='id')*

Custom primary key to prevent conflicts with the proxy model's primary key.

<hr/>

### *class* curation.models.CuratedItemManager

A manager that defines queryset helpers for CuratedItem.

##### group(*slug*)

Filter the current queryset to rows with curated groups having slug "slug".

<hr/>

### *class* **curation.base.CuratedItemModelBase**

Overrides **ModelBase** to check whether a **curation.fields.CuratedForeignKey**
is defined on the model. If not, throw a **TypeError**.

<hr/>

### *class* **curation.fields.CuratedForeignKey**

A ForeignKey that gets a list of the `__dict__` keys and field names of the
related model on load. It saves this list to the `_proxy_attrs` attribute of
its parent model's `_meta` attribute.

##### contribute_to_class(*cls, name*)

A django built-in that adds attributes to the model class in which it is
defined.

This method sets the `_curated_proxy_field_name` on the `_meta` attribute
of the **CuratedForeignKey**'s parent model to the field's name (e.g. "post"
in the example at the very beginning of this README).

##### contribute_to_related_class(*cls, related*)

A django built-in that adds attributes to the class a **RelatedField**
points to.

In this case we're adding `_proxy_attrs` to the _meta attribute of the 
**ForeignKey**'s parent model, not the related model. The reason we're not
using `contribute_to_class` is that we need the related class to be
instantiated to obtain its field names, and the related class may not be loaded
yet when `contribute_to_class` is called (for instance, if it is lazy loaded,
when the ForeignKey field is defined using a string for the model).

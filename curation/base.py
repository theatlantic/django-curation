from warnings import warn

from django.db.models.base import ModelBase
from django.db.models.fields import FieldDoesNotExist

from .fields import CuratedForeignKey

class CuratedItemModelBase(ModelBase):
    """
    Overrides ModelBase to check whether a CuratedForeignKey is defined on
    the model. If not, throw a TypeError.
    """
    def __new__(cls, name, bases, attrs):
        # The cls in the method class isn't a typo, that's just how `__new__`
        # works with super()
        model_cls = super(CuratedItemModelBase, cls).__new__(cls, name, bases, attrs)

        if model_cls._meta.abstract:
            return model_cls

        from .models import CuratedItem

        # If someone was silly and used this metaclass on something that
        # doesn't extend CuratedItem, just return the super.
        if not issubclass(model_cls, CuratedItem):
            warn("Model %r has __metaclass__ CuratedItemModelBase, but it does"
                 " not extend CuratedItem." % model_cls._meta.object_name)
            return model_cls

        if not hasattr(model_cls._meta, '_curated_proxy_field_name'):
            raise TypeError("Model %r has no CuratedForeignKey fields. All "
                            "subclasses of CuratedItem must define exactly "
                            "one CuratedForeignKey field." %
                                model_cls._meta.object_name)
        return model_cls

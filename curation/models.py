from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from .base import CuratedItemModelBase

class CuratedGroup(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=75,
        help_text="Used for database slug")

    class Meta:
        abstract = True
        verbose_name = "Curated Content"
        verbose_name_plural = "Curated Content"

    def __unicode__(self):
        return u"%s" % self.name


class CuratedItemManager(models.Manager):
    """A manager that defines queryset helpers for CuratedItem."""

    def group(self, slug):
        """
        Filter the current queryset to rows belonging to curated groups
        having slug ``slug``.
        """
        return self.filter(group__slug=slug)


class CuratedItem(models.Model):
    """
    Abstract class representing an item in a curated group.

    In order for models which extend this class to proxy successfully, they
    must define a `CuratedForeignKey` field, e.g.::

        post = curation.fields.CuratedForeignKey(Post)
    """

    __metaclass__ = CuratedItemModelBase

    #: A dict that maps field names in the proxy model (the to=... model in the
    #: CuratedForeignKey) to field names in the current model which can
    #: override them (provided their value is not None or an empty string).
    #: 
    #: This takes the form, e.g.::
    #: 
    #:     field_overrides = {
    #:         'title': 'custom_title',
    #:         'status': 'custom_status',
    #:     }
    #: 
    #: Where ``custom_title`` and ``custom_status`` are fields in the
    #: CuratedItem model, and ``title`` and ``status`` are fields in the
    #: proxy model.
    field_overrides = {}

    #: Custom Primary Key
    primary_id = models.AutoField(primary_key=True, db_column='id')

    position = models.PositiveSmallIntegerField("Position")

    class Meta:
        abstract = True
        ordering = ['position']

    def __getattr__(self, attr):
        """
        When this object doesn't have a property:

        1. Check if it exists in field_overrides. If so, change the attribute
           being checked to field_overrides[attr]. If the current class has a
           value for this attribute and it is not None and != '', return the
           value.
        2. Check if the attr is in self._meta._proxy_attrs. If so, return the
           value for that attribute in the proxy field.
        """
        # If self.field_overrides[attr] == attr, we would get an infinite loop
        if attr in self.field_overrides and self.field_overrides[attr] != attr:
            val = getattr(self, self.field_overrides[attr])
            if val is not None and val != '':
                return val
        if attr in getattr(self._meta, '_proxy_attrs', []):
            try:
                item = getattr(self, self._meta._curated_proxy_field_name)
            except ObjectDoesNotExist:
                pass
            else:
                return getattr(item, attr)

        raise AttributeError("'%s' object has no attribute '%s'" % \
            (self.__class__.__name__, attr))


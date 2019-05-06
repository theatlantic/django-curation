from __future__ import absolute_import
from django.db import models
from django.utils import six
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


class CuratedItem(six.with_metaclass(CuratedItemModelBase, models.Model)):
    """
    Abstract class representing an item in a curated group.

    In order for models which extend this class to proxy successfully, they
    must define a `CuratedForeignKey` field, e.g.::

        post = curation.fields.CuratedForeignKey(Post)
    """

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
        2. Check if self._meta._curated_field_is_generic is True. If so, check
           if the attr is in self._proxy_attrs (for an explanation of why
           the CuratedGenericForeignKey uses _proxy_attrs on the model
           instance rather than the model _meta, see the docstring in
           curation.fields.CuratedRelation.contribute_to_instance()).
           If attr is in self._proxy_attrs, return the value for that
           attribute in the proxy field.
        3. If the CuratedRelatedField on the model is not a
           CuratedGenericForeignKey, check if the attr is in
           self._meta._proxy_attrs. If so, return the value for that attribute
           in the proxy field.
        """

        # We would get an infinite loop if self.field_overrides[attr] == attr
        if attr in self.field_overrides and self.field_overrides[attr] != attr:
            val = getattr(self, self.field_overrides[attr])
            if val or isinstance(val, bool):
                return val

        proxy_attrs = []

        opts = self._meta

        curated_field_name = getattr(opts, '_curated_proxy_field_name', None)
        is_generic_curated_field = getattr(opts, '_curated_field_is_generic', False)

        is_cache_attr = (attr[0] == '_' and attr.endswith('_cache'))

        if is_cache_attr:
            try:
                return self.__dict__[attr]
            except KeyError:
                pass
        elif is_generic_curated_field:
            try:
                proxy_attrs = self.__dict__['_proxy_attrs']
            except KeyError:
                # Call __get__() on CuratedGenericForeignKey descriptor, which
                # populates _proxy_attrs by calling contribute_to_instance()
                self.__getattribute__(curated_field_name)
                proxy_attrs = self.__dict__.get('_proxy_attrs', [])
        else:
            proxy_attrs = getattr(getattr(self, curated_field_name)._meta, '_proxy_attrs', [])

        if attr in proxy_attrs:
            try:
                item = getattr(self, curated_field_name)
            except ObjectDoesNotExist:
                raise
            else:
                try:
                    return getattr(item, attr)
                except AttributeError:
                    if is_generic_curated_field is not None:
                        if getattr(self, '_proxy_model', None) is not None:
                            opts = self._meta
                            proxy_opts = self._proxy_model._meta
                            curated_field = [f for f in opts.virtual_fields
                                             if f.name == curated_field_name][0]
                            fk = getattr(self, curated_field.fk_field)
                            if fk:
                                fk_str = u" and pk=%d" % fk
                            else:
                                fk_str = u""

                            raise self._proxy_model.DoesNotExist((
                                u"CuratedGenericForeignKey field %(field)r "
                                u"on %(app_label)s.%(model_name)s with model "
                                u"'%(rel_app_label)s.%(rel_model_name)s'"
                                u"%(fk_str)s does not exist") % {
                                    "rel_app_label": proxy_opts.app_label,
                                    "rel_model_name": proxy_opts.object_name,
                                    "field": curated_field_name,
                                    "app_label": self._meta.app_label,
                                    "model_name": self._meta.object_name,
                                    "fk_str": fk_str})

        raise AttributeError("'%s' object has no attribute '%s'" %
            (self.__class__.__name__, attr))

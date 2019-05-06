from __future__ import absolute_import
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import signals
from django.contrib.contenttypes.fields import GenericForeignKey as _GenericForeignKey


class GenericForeignKey(_GenericForeignKey):
    """
    Provides a generic relation to any object through content-type/object-id
    fields.

    Overrides the parent to allow generic foreign keys that point to models
    on other databases, and so that it can hook into the proxy attributes
    of curation.fields.CuratedRelation.
    """

    def contribute_to_class(self, cls, name):
        super(GenericForeignKey, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.instance_post_init, sender=cls)

        if not cls._meta.proxy:
            signals.class_prepared.connect(self.relate_fk_field_to_ct_field, sender=cls)

    def relate_fk_field_to_ct_field(self, sender, **kwargs):
        """
        Handles the class_prepared signal; adds an attribute `fk_field` to
        the content_type Field object containing the field name of the
        object_id (`fk_field`) Field.
        """
        ct_field = sender._meta.get_field(self.ct_field)
        ct_field.fk_field = self.fk_field

    def instance_post_init(self, instance, force=False, *args, **kwargs):
        ct = getattr(instance, self.ct_field)
        if ct and hasattr(self, 'contribute_to_instance'):
            try:
                model_cls = ct.model_class()
            except IndexError:
                pass
            else:
                self.contribute_to_instance(instance, model_cls)

    def get_content_type(self, obj=None, id=None, using=None):
        """
        Identical to parent method except uses our proxy model of ContentType
        that works with generic contenttypes in multiple databases.
        """
        from django.contrib.contenttypes.models import ContentType
        if obj:
            using = obj._state.db
            return ContentType.objects.db_manager(using).get_for_model(obj, False)
        elif id:
            return ContentType.objects.db_manager(using).get_for_id(id)
        else:
            # This should never happen. I love comments like this, don't you?
            raise Exception("Impossible arguments to GFK.get_content_type!")

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        try:
            # Avoid an infinite loop from CuratedItem.__getattr__() by using
            # __dict__ instead of getattr()
            return instance.__dict__[self.cache_attr]
        except KeyError:
            rel_obj = None

            f = self.model._meta.get_field(self.ct_field)
            ct_id = getattr(instance, f.get_attname(), None)
            if ct_id:
                ct = self.get_content_type(id=ct_id, using=instance._state.db)
                # This code is specific to django-curation. It calls
                # contribute_to_instance with the model class of the foreign
                # content-type
                if ct and hasattr(self, 'contribute_to_instance'):
                    try:
                        model_cls = ct.model_class()
                    except IndexError:
                        pass
                    else:
                        self.contribute_to_instance(instance, model_cls)
                try:
                    rel_obj = ct.get_object_for_this_type(pk=getattr(instance,
                        self.fk_field))
                except ObjectDoesNotExist:
                    pass
            setattr(instance, self.cache_attr, rel_obj)
            return rel_obj

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(u"%s must be accessed via instance"
                                       % self.related.opts.object_name)
        ct = None
        fk = None
        if value is not None:
            ct = self.get_content_type(obj=value)
            # This code is specific to django-curation. It calls
            # contribute_to_instance with the model class of the foreign
            # content-type
            if ct and hasattr(self, 'contribute_to_instance'):
                try:
                    model_cls = ct.model_class()
                except IndexError:
                    pass
                else:
                    self.contribute_to_instance(instance, model_cls)

            fk = value._get_pk_val()

        setattr(instance, self.ct_field, ct)
        setattr(instance, self.fk_field, fk)
        setattr(instance, self.cache_attr, value)

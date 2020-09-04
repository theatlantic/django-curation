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

        f = self.model._meta.get_field(self.ct_field)
        ct_id = getattr(instance, f.get_attname(), None)
        pk_val = getattr(instance, self.fk_field)

        rel_obj = self.get_cached_value(instance, default=None)
        if rel_obj is not None:
            if ct_id != self.get_content_type(obj=rel_obj, using=instance._state.db).id:
                rel_obj = None
            else:
                pk = rel_obj._meta.pk
                # If the primary key is a remote field, use the referenced
                # field's to_python().
                to_python_field = pk
                # Out of an abundance of caution, avoid infinite loops.
                seen = {to_python_field}
                while to_python_field.remote_field:
                    to_python_field = to_python_field.target_field
                    if to_python_field in seen:
                        break
                    seen.add(to_python_field)
                pk_to_python = to_python_field.to_python
                if pk_to_python(pk_val) != rel_obj._get_pk_val():
                    rel_obj = None
                else:
                    return rel_obj

        if ct_id is not None:
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
                rel_obj = ct.get_object_for_this_type(pk=pk_val)
            except ObjectDoesNotExist:
                pass
        self.set_cached_value(instance, rel_obj)
        return rel_obj

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(
                "%s must be accessed via instance" % self.related.opts.object_name)

        ct = None
        fk = None
        if value is not None:
            ct = self.get_content_type(obj=value)
            fk = value.pk

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

        setattr(instance, self.ct_field, ct)
        setattr(instance, self.fk_field, fk)
        self.set_cached_value(instance, value)

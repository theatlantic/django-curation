from django.db.models.fields.related import ForeignKey

class CuratedForeignKey(ForeignKey):
    """
    A ForeignKey that gets a list of the __dict__ keys and field names of the
    related model on load. It saves this list to the '_proxy_attrs' attribute
    of its parent model _meta attribute.
    """
    def contribute_to_class(self, cls, name):
        super(CuratedForeignKey, self).contribute_to_class(cls, name)
        # Throw a TypeError if there is more than one CuratedForeignKey in
        # the model
        if hasattr(cls._meta, '_curated_proxy_field_name'):
            proxy_field = getattr(cls._meta, '_curated_proxy_field_name')
            raise TypeError('Model %r has more than one CuratedForeignKey: '
                            '%r and %r' % (cls.__name__, proxy_field, name))
        setattr(cls._meta, '_curated_proxy_field_name', name)

    def contribute_to_related_class(self, cls, related):
        """
        A django built-in that adds attributes to the class a RelatedField
        points to.

        In this case we're adding '_proxy_attrs' to the _meta attribute of the
        ForeignKey's parent model, not the related model. The reason we're not
        using `contribute_to_class` is that we need the related class to be
        instantiated to obtain its field names, and the related class may not
        be loaded yet when `contribute_to_class` is called (for instance, if
        it is lazy loaded, when the ForeignKey field is defined using a string
        for the model).
        """
        super(CuratedForeignKey, self).contribute_to_related_class(cls, related)
        skips = ('DoesNotExist', 'MultipleObjectsReturned', '__doc__', '_meta',
                 '__module__', '_base_manager', '_default_manager', 'objects',)
        proxy_attrs = set([f.name for f in cls._meta.fields])
        proxy_attrs = proxy_attrs.union([k for k in cls.__dict__ if k not in skips])
        setattr(related.model._meta, '_proxy_attrs', proxy_attrs)
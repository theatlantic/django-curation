import textwrap
import json

from django.urls import reverse, NoReverseMatch
from django.apps import apps
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.cache import never_cache

from django.contrib.contenttypes.models import ContentType

# The version of django.contrib.contenttypes.views.shortcut with a bug fixed
# for multi-db setups
from .contenttypes import shortcut  # noqa


ct_vals = ContentType.objects.all().values('pk', 'app_label', 'model')


def get_label(f):
    if getattr(f, "related_label", None):
        return f.related_label()
    else:
        return str(f)


def get_common_field_values(curated_item_cls, fk_obj):
    field_overrides = getattr(curated_item_cls, 'field_overrides', {})
    override_field_names = list(field_overrides.keys())
    curated_fields = set([f.name for f in curated_item_cls._meta.fields])
    curated_fields = curated_fields.union(set(override_field_names))
    fk_fields = set([f.attname for f in fk_obj._meta.fields
                     if f.name in curated_fields])
    fk_data = {}
    for field_name in fk_fields:
        try:
            value = getattr(fk_obj, field_name, None)
        except:
            pass

        # If the field is a FileField, get the name of the file
        # as the value, so it can be converted to json.
        if hasattr(value, 'file') and hasattr(value.file, 'name'):
            value = value.file.name

        if value != "" and value != "":
            if field_name in field_overrides:
                field_name = field_overrides[field_name]
            fk_data[field_name] = value
    return fk_data


def get_curated_item_for_request(request):
    data = {}
    app_label = request.GET.get('app_label')
    model_name = request.GET.get('model_name')
    try:
        ct_field = str(request.GET.get('ct_field'))
        fk_field = str(request.GET.get('fk_field'))
    except UnicodeEncodeError:
        return None

    # At some point, do something with this validation
    try:
        object_id = int(request.GET.get('object_id'))
        model_ct_id = int(request.GET.get('ct_id'))
    except (TypeError, ValueError):
        return None

    ct_model_cls = apps.get_model(app_label, model_name)
    if ct_model_cls is None:
        return data
    ct_id = ContentType.objects.get_for_model(ct_model_cls, False)

    try:
        model_content_type = ContentType.objects.get_for_id(model_ct_id)
    except ContentType.DoesNotExist:
        return None

    model_cls = model_content_type.model_class()
    init_kwargs = {
        ct_field: ct_id,
        fk_field: object_id,
    }
    curated_item = model_cls(**init_kwargs)
    curated_field_name = getattr(model_cls._meta, '_curated_proxy_field_name', None)
    if curated_field_name is None:
        return None

    fk_data = None
    try:
        fk_obj = getattr(curated_item, curated_field_name)
    except:
        pass
    else:
        if fk_obj:
            fk_data = get_common_field_values(model_cls, fk_obj)

    data.update({"fk": fk_data})

    try:
        obj = ct_model_cls.objects.get(pk=object_id)
    except ct_model_cls.DoesNotExist:
        return None
    else:
        data.update({
            "value": obj.pk,
            "label": get_label(obj),
        })
    return [data]


def empty_json(obj):
    """
    If we don't know how to serialize an object, just return `None`
    instead of throwing `TypeError: <whatever> is not JSON serializable`.
    """

    return None


@never_cache
def related_lookup(request):
    if not (request.user.is_active and request.user.is_staff):
        return HttpResponseForbidden('<h1>Permission denied</h1>')
    data = []
    required_params = ('app_label', 'model_name', 'object_id', 'ct_field', 'fk_field', 'ct_id',)

    if request.method == 'GET':
        if all([request.GET.get(k) for k in required_params]):
            data = get_curated_item_for_request(request)
            if data is not None:
                return HttpResponse(json.dumps(data, default=empty_json),
                    content_type='application/javascript')

    data = [{"value": None, "label": ""}]
    return HttpResponse(json.dumps(data),
        content_type='application/javascript')


related_lookup_url = None
shortcut_url = None
content_types = None


def get_content_types(request):
    if not (request.user.is_active and request.user.is_staff):
        return HttpResponseForbidden('"Permission denied"')

    global content_types, related_lookup_url, shortcut_url

    if related_lookup_url is None:
        related_lookup_url = reverse('curation_related_lookup')

    if shortcut_url is None:
        shortcut_url = reverse('curation_shortcut', kwargs={
            'content_type_id': 0,
            'object_id': 0,
        }).replace('/0/0', '/{0}/{1}')

    if content_types is None:
        content_types = {}
        for ct in ct_vals:
            try:
                ct['changelist'] = reverse(
                    'admin:%s_%s_changelist' % (ct['app_label'], ct['model']))
            except NoReverseMatch:
                pass
            content_types[ct['pk']] = ct

    # flake8: noqa: W605
    ct_js = textwrap.dedent("""
        var DJCURATION = (typeof window.DJCURATION != "undefined")
                       ? DJCURATION : {};
        DJCURATION.CONTENT_TYPES = %s;
        DJCURATION.LOOKUP_URL = %s;

        (function() {
            var urlTemplate = %s,
                templateRegex = /\{(\d+)\}/gm;

            DJCURATION.getShortcutUrl = function(contentTypeId, objectId) {
                var args = [contentTypeId, objectId];
                return urlTemplate.replace(templateRegex, function(match, p1, offset, string) {
                    return (args[p1]) ? args[p1] : '0';
                });
            };

            DJCURATION.getContentType = function(app_label, model) {
                for (var id in DJCURATION.CONTENT_TYPES) {
                    var ct = DJCURATION.CONTENT_TYPES[id];
                    if (ct.app_label == app_label && ct.model == model) {
                        return ct;
                    }
                }
            };

        })();""" % (
            json.dumps(content_types),
            json.dumps(related_lookup_url),
            json.dumps(shortcut_url),))
    return HttpResponse(ct_js.strip(), content_type='application/javascript')

import textwrap

from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.simplejson import simplejson
from django.views.decorators.cache import never_cache

from .models import ContentType


ct_ids = [v[0] for v in ContentType.objects.all().values_list('id')]


def get_label(f):
    get_label_func = getattr(f, "related_label", f.__unicode__)
    return get_label_func()

def get_common_field_values(curated_item_cls, fk_obj):
    field_overrides = getattr(curated_item_cls, 'field_overrides', {})
    override_field_names = field_overrides.keys()
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
        if value is not u"" and value is not "":
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

    ct_model_cls = models.get_model(app_label, model_name)
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

    try:
        fk_obj = getattr(curated_item, curated_field_name)
    except:
        fk_data = None
    else:
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
                return HttpResponse(simplejson.dumps(data),
                    mimetype='application/javascript')

    data = [{"value": None, "label": ""}]
    return HttpResponse(simplejson.dumps(data),
        mimetype='application/javascript')

def get_content_types(request):
    if not (request.user.is_active and request.user.is_staff):
        return HttpResponseForbidden('"Permission denied"')

    content_types = {}
    for ct_id in ct_ids:
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except AttributeError:
            pass
        else:
            try:
                content_types[ct_id] = {
                    'pk': ct_id,
                    'app': ct.app_label,
                    'model': ct.model,
                    'changelist': reverse('admin:%s_%s_changelist' % (
                        ct.app_label, ct.model))}
            except NoReverseMatch:
                pass

    related_lookup_url = reverse('curation_related_lookup')

    ct_js = textwrap.dedent(u"""
        var DJCURATION = (typeof window.DJCURATION != "undefined")
                       ? DJCURATION : {};
        DJCURATION.CONTENT_TYPES = %s;
        DJCURATION.LOOKUP_URL = %s;""" % (
            simplejson.dumps(content_types),
            simplejson.dumps(related_lookup_url),))
    return HttpResponse(ct_js.strip(), mimetype='application/javascript')

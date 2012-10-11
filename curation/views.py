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


@never_cache
def related_lookup(request):
    if not (request.user.is_active and request.user.is_staff):
        return HttpResponseForbidden('<h1>Permission denied</h1>')
    data = []
    required_params = ('app_label', 'model_name', 'object_id',)

    if request.method == 'GET':
        if all([request.GET.get(k) for k in required_params]):
            object_id = request.GET.get('object_id')
            app_label = request.GET.get('app_label')
            model_name = request.GET.get('model_name')
            try:
                model = models.get_model(app_label, model_name)
                obj = model.objects.get(pk=object_id)
                data.append({
                    "value": obj.id,
                    "label": get_label(obj),
                })
                return HttpResponse(simplejson.dumps(data),
                    mimetype='application/javascript')
            except:
                pass

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

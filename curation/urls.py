import functools
from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from . import views as curation_views


def wrap(view, cacheable=False):
    """
    From django.contrib.admin.sites.get_urls()
    """
    def wrapper(*args, **kwargs):
        return admin.sites.site.admin_view(view, cacheable)(*args, **kwargs)
    return functools.update_wrapper(wrapper, view)


urlpatterns = patterns('',
    url(r'^content-type-list\.js$',
        wrap(curation_views.get_content_types), # 'curation.views.get_content_types',
        name="curation_content_type_list"),
    url(r'^lookup/related/$',
        wrap(curation_views.related_lookup), # 'curation.views.related_lookup',
        name="curation_related_lookup"),
    url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$',
        wrap(curation_views.shortcut),
        name="curation_shortcut"),
)

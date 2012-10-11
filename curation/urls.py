from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
    url(r'^content-type-list\.js$', 'curation.views.get_content_types',
        name="curation_content_type_list"),
    url(r'^lookup/related/$', 'curation.views.related_lookup',
        name="curation_related_lookup"),
)


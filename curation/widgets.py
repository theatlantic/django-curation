from collections import Mapping

from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms import widgets
try:
    from django.forms.utils import flatatt
except ImportError:
    from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape


class SourceSelect(widgets.Select):

    def _media(self):
        media = widgets.Media()
        media.add_js((
            reverse('curation_content_type_list'),
            settings.STATIC_URL + 'curation/curated_related_generic.js?v=2',
            settings.STATIC_URL + 'curation/curation.js?v=1',))
        media.add_css({
                'all': (settings.STATIC_URL + 'curation/curation.css',)})
        return media
    media = property(_media)

    def render_option(self, selected_choices, option_value, option_label):
        if isinstance(option_value, Mapping) and 'value' in option_value:
            value = force_unicode(option_value['value'])
            if value in selected_choices:
                selected_html = u' selected="selected"'
            else:
                selected_html = ''
            return u'<option%s%s>%s</option>' % (
                flatatt(option_value), selected_html,
                conditional_escape(force_unicode(option_label)))
        else:
            return super(SourceSelect, self).render_option(selected_choices,
                option_value, option_label)

from __future__ import absolute_import
from itertools import chain

from django.urls import reverse
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import conditional_escape


class SourceSelect(widgets.Select):

    def _media(self):
        media = widgets.Media()
        media.add_js((
            reverse('curation_content_type_list'),
            'curation/curated_related_generic.js',
            'curation/curation.js',))
        media.add_css({
                'all': ('curation/curation.css',)})
        return media
    media = property(_media)

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget (Django 1.11)"""
        # Unfortunately there isn't a better way to perform the override
        # we previously did in the render_option() method in Django 1.11
        # besides copying and modifying ChoiceWidget.optgroups
        groups = []
        has_selected = False
        for index, (option_value, option_label) in enumerate(chain(self.choices)):
            option_attrs = {}
            try:
                option_value.get('value')
            except:
                pass
            else:
                option_attrs = dict(option_value)
                option_value = option_attrs.pop('value', None)

            if option_value is None:
                option_value = ''

            selected = force_text(option_value) in value and has_selected is False
            if selected is True and has_selected is False:
                has_selected = True
            option = self.create_option(
                name, option_value, option_label, selected, index,
                subindex=None, attrs=attrs)
            option['attrs'].update(option_attrs)
            groups.append((None, [option], index))

        return groups

    def render_option(self, selected_choices, option_value, option_label):
        try:
            option_value.get('value')
        except:
            return super(SourceSelect, self).render_option(selected_choices,
                option_value, option_label)
        else:
            option_attrs = dict(option_value)
            option_value = force_text(option_attrs.get('value'))
            if option_value in selected_choices:
                selected_html = u' selected="selected"'
            else:
                selected_html = ''
            return u'<option%s%s>%s</option>' % (
                flatatt(option_attrs), selected_html,
                conditional_escape(force_text(option_label)))

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

class RichTextEditor(forms.Textarea):
    def render(self, name, value, attrs=None):
        return mark_safe(render_to_string("wysihtml5/widget.html", {
            "name": name,
            "value": value,
            "attrs": attrs,
        }))

    class Media:
        css = {'all': (settings.STATIC_URL + "wysihtml5/toolbar.css",)}
        js = (
            settings.STATIC_URL + "wysihtml5/wysihtml-0.4.17/dist/wysihtml5x-toolbar.min.js",
            settings.STATIC_URL + "wysihtml5/wysihtml-0.4.17/parser_rules/advanced_and_extended.js",
            settings.STATIC_URL + "wysihtml5/init.js",
        )
           


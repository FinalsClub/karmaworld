# Snippet from
# https://djangosnippets.org/snippets/2916/
"""
Add the line to settings.py::

    SERIALIZATION_MODULES = {'json-pretty': 'serializers.json_pretty'}

And call dumpdata as follows::

    ./manage.py dumpdata --format=json-pretty <app_name>

"""

from django.core.serializers.json import Serializer as JSONSerializer


class Serializer(JSONSerializer):
    def start_serialization(self):
        super(Serializer, self).start_serialization()
        self.json_kwargs['ensure_ascii'] = False

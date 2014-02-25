from django import template

register = template.Library()

@register.filter(name='get')
def get(obj, key):
    """ Call getitem against the given key. """
    return obj[key]

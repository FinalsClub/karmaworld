from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def toolbar_button(command, icon=None, alt=None, value=None, classes="button secondary"):
    if icon is None:
        icon = command
    if alt is None:
        alt = command
    if value is None:
        value = ""
    else:
        value = "data-wysihtml5-command-value='{}'".format(value)
    button = mark_safe("""<button role='button'
            class='{classes}'
            data-wysihtml5-command='{command}'
            {value}><i class='fa fa-{icon}' aria-label='{alt}'></i></button>""".format(
        command=command,
        value=value,
        icon=icon,
        alt=alt,
        classes=classes
    ))
    print button
    return button



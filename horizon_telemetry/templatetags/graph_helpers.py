from django import template

register = template.Library()


@register.filter(name='replace')
def replace(value, arg=None):
    return value.replace('.', '_').replace('-', '_')

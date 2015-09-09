from django import template

register = template.Library()

@register.assignment_tag
def as_tuple(*args):
    return tuple(args)
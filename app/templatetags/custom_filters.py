from django import template

register = template.Library()

@register.filter
def split_lines(value):
    """Split a string by newlines and return a list"""
    if value:
        return value.split('\n')
    return ['']
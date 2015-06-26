from django import template

register = template.Library()

@register.filter
def field_in_dictionary(row, key):
    return row.get(key, '')

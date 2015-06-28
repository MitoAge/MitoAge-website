from django import template

from mitoage.analysis.models import BaseComposition


register = template.Library()

@register.filter
def field_in_dictionary(row, key):
    return row.get(key, '')

@register.filter
def base_composition_nice_title(key):
    return BaseComposition.get_nice_title(key)
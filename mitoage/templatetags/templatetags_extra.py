from decimal import Decimal

from django import template

from mitoage.analysis.models import BaseComposition, CodonUsage, MitoAgeEntry


register = template.Library()

@register.filter
def field_in_dictionary(row, key):
    return row.get(key, '0')


@register.filter
def per_1kb(value, size):
    return int(round(value*1000.0/size, 0)) if value and size else None

@register.simple_tag
def percent(value, size, digits):
    value = Decimal(value)
    if not value:
        return 0
    return round(value*100/size, digits) if value and size else None


@register.filter
def total_lower(value):
    return BaseComposition.total_title_lower(value)

@register.filter
def base_composition_nice_title(key):
    return BaseComposition.get_nice_title(key)

@register.filter
def codon_usage_nice_title(key):
    return CodonUsage.get_nice_title(key)


@register.filter
def pluralize_taxonomy(key):
    return {'species':'species', 'family':'families', 'order':'orders', 'class':'classes'}.get(key, key)

@register.filter
def get_aa_url(symbol):
    return "images/aa_icons/%s.png" % symbol


@register.filter
def get_base_composition(species, section):
    if not species:
        return None
    try:
        mitoage_entry = species.mitoage_entries.first()
        if mitoage_entry:
            return mitoage_entry.get_base_composition(section)
    except MitoAgeEntry.DoesNotExist:
        pass
    return None
    
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from mitoage.taxonomy.models import TaxonomySpecies, TaxonomyFamily, \
    TaxonomyOrder, TaxonomyClass


def statistics(request):
    nr_of_species = TaxonomySpecies.objects.all().count()
    nr_of_families = TaxonomyFamily.objects.all().count()
    nr_of_orders = TaxonomyOrder.objects.all().count()
    nr_of_classes = TaxonomyClass.objects.all().count()

    nr_of_species = TaxonomySpecies.objects.all().count()
    
    
    return render_to_response('analysis/statistics.html', locals(), RequestContext(request))

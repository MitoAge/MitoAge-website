from django.db import connection
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from mitoage.analysis.models import MitoAgeEntry, BaseCompositionStats
from mitoage.taxonomy.models import TaxonomySpecies, TaxonomyFamily, \
    TaxonomyOrder, TaxonomyClass


def statistics(request):
    no_of_species = TaxonomySpecies.objects.all().count()
    no_of_families = TaxonomyFamily.objects.all().count()
    no_of_orders = TaxonomyOrder.objects.all().count()
    no_of_classes = TaxonomyClass.objects.all().count()
    
    species_max_ls = TaxonomySpecies.objects.order_by('-lifespan')[0]
    species_min_ls = TaxonomySpecies.objects.order_by('lifespan')[0]
    
    entry_max_size = MitoAgeEntry.objects.order_by('-bc_total_mtDNA_size')[0]
    entry_min_size = MitoAgeEntry.objects.order_by('bc_total_mtDNA_size')[0]
    
    cursor = connection.cursor()
    cursor.execute('SELECT "analysis_mitoageentry"."species_id", ("analysis_mitoageentry"."bc_total_mtDNA_g"+"analysis_mitoageentry"."bc_total_mtDNA_c")*100.0 / "analysis_mitoageentry"."bc_total_mtDNA_size" AS gc_percent  FROM "analysis_mitoageentry" ORDER BY "gc_percent" DESC')
    (max_gc_species_id, max_gc) = cursor.fetchone()
    max_gc_species = TaxonomySpecies.objects.get(id=max_gc_species_id)

    cursor.execute('SELECT "analysis_mitoageentry"."species_id", ("analysis_mitoageentry"."bc_total_mtDNA_g"+"analysis_mitoageentry"."bc_total_mtDNA_c")*100.0 / "analysis_mitoageentry"."bc_total_mtDNA_size" AS gc_percent  FROM "analysis_mitoageentry" ORDER BY "gc_percent"')
    (min_gc_species_id, min_gc) = cursor.fetchone()
    min_gc_species = TaxonomySpecies.objects.get(id=min_gc_species_id)

    max_at = 100 - min_gc
    max_at_species = min_gc_species

    min_at = 100 - max_gc
    min_at_species = max_gc_species
    
    return render_to_response('analysis/statistics.html', locals(), RequestContext(request))

def compare(request):
    compared_stats = request.session.get('compared_stats', [])
    compared_stats = BaseCompositionStats.get_cached_objects(compared_stats)
    return render_to_response('analysis/compare.html', locals(), RequestContext(request))

def add_to_compare_cart(request, pk):
    compared_stats = request.session.get('compared_stats', [])
    if pk not in compared_stats:
        compared_stats.append(pk)
        request.session['compared_stats'] = compared_stats
    
    from django.http import JsonResponse
    return JsonResponse({'no_compared_stats':len(request.session['compared_stats'])})

def delete_from_compare_cart(request, pk):
    compared_stats = request.session.get('compared_stats', [])
    if pk in compared_stats:
        compared_stats.remove(pk)
        request.session['compared_stats'] = compared_stats
    compared_stats = BaseCompositionStats.get_cached_objects(compared_stats)
    return render_to_response('analysis/compare.html', locals(), RequestContext(request))

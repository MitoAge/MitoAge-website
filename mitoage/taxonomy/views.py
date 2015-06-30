from django.core.context_processors import request
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView

from mitoage.analysis.models import MitoAgeEntry, BaseComposition, CodonUsage
from mitoage.taxonomy.models import TaxonomyClass, TaxonomyOrder, TaxonomyFamily, \
    TaxonomySpecies
from mitoage.taxonomy.utils import get_query


class SpeciesView(object):
    #queryset = Gallery.objects.filter(is_public=True)
    pass

class SpeciesListView(SpeciesView, ListView):
    paginate_by = 20


####################################
#             Taxonomy             #
####################################

class Breadcrumb():

    def __init__(self, name, named_url, obj):
        self.name = name
        if obj:
            self.url = reverse_lazy(named_url, args=[obj.pk])
        else:
            self.url = reverse_lazy(named_url)


class BrowseAllClassesList(ListView):
    model = TaxonomyClass
    template_name = "browsing/taxonomy_class_list.html"
    paginate_by = 45
    
    def get_context_data(self, **kwargs):
        context = super(BrowseAllClassesList, self).get_context_data(**kwargs)
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "", None),]
        return context


class TaxonomyClassDetail(SingleObjectMixin, ListView):
    template_name = "browsing/taxonomy_class_detail.html"
    model = TaxonomyClass
    paginate_by = 45

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=TaxonomyClass.objects.all())
        return super(TaxonomyClassDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaxonomyClassDetail, self).get_context_data(**kwargs)
        context['taxonomy_class'] = self.object
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.name, "", None),]
        return context

    def get_queryset(self):
        return self.object.taxonomy_orders.all()

class TaxonomyOrderDetail(SingleObjectMixin, ListView):
    template_name = "browsing/taxonomy_order_detail.html"
    model = TaxonomyOrder
    paginate_by = 45

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=TaxonomyOrder.objects.all())
        return super(TaxonomyOrderDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaxonomyOrderDetail, self).get_context_data(**kwargs)
        context['taxonomy_order'] = self.object
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.taxonomy_class.name, "browse_class", self.object.taxonomy_class),
                                  Breadcrumb(self.object.name, "", None),]
        return context

    def get_queryset(self):
        return self.object.taxonomy_families.all()

class TaxonomyFamilyDetail(SingleObjectMixin, ListView):
    template_name = "browsing/taxonomy_family_detail.html"
    model = TaxonomyFamily
    paginate_by = 45

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=TaxonomyFamily.objects.all())
        return super(TaxonomyFamilyDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaxonomyFamilyDetail, self).get_context_data(**kwargs)
        context['taxonomy_family'] = self.object
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.taxonomy_order.taxonomy_class.name, "browse_class", self.object.taxonomy_order.taxonomy_class),
                                  Breadcrumb(self.object.taxonomy_order.name, "browse_order", self.object.taxonomy_order),
                                  Breadcrumb(self.object.name, "", None),]
        return context

    def get_queryset(self):
        return self.object.taxonomy_species.all()


class TaxonomySpeciesDetail(DetailView):
    template_name = "browsing/taxonomy_species_detail.html"
    model = TaxonomySpecies

    def get_context_data(self, **kwargs):
        context = super(TaxonomySpeciesDetail, self).get_context_data(**kwargs)
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.taxonomy_family.taxonomy_order.taxonomy_class.name, "browse_class", self.object.taxonomy_family.taxonomy_order.taxonomy_class),
                                  Breadcrumb(self.object.taxonomy_family.taxonomy_order.name, "browse_order", self.object.taxonomy_family.taxonomy_order),
                                  Breadcrumb(self.object.taxonomy_family.name, "browse_family", self.object.taxonomy_family),
                                  Breadcrumb(self.object.name, "", None),]
        context['base_compositions'] = self.get_base_compositions(self.object)
        context['general_sections'] = ["total_mtDNA", "total_pc_mtDNA", "d_loop_mtDNA", "total_rRNA_mtDNA", "rRNA_12S", "rRNA_16S"]
        context['gene_sections'] = ['atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6']
        context['codon_usages'] = self.get_codon_usages(self.object)
        context['codon_usage_sections'] = ['total_pc_mtDNA', 'atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6']
        return context

    def get_base_compositions(self, species):
        try:
            mitoage_entry = species.mitoage_entries.first()
            if mitoage_entry:
                return mitoage_entry.get_base_compositions_as_dictionaries()
        except MitoAgeEntry.DoesNotExist:
            pass
        return {key: None for key in BaseComposition.get_bc_sections()}

    def get_codon_usages(self, species):
        try:
            mitoage_entry = species.mitoage_entries.first()
            if mitoage_entry:
                return mitoage_entry.get_codon_usages_as_dictionaries()
        except MitoAgeEntry.DoesNotExist:
            pass
        return {key: None for key in CodonUsage.get_cu_sections()}

def search(request):
    query_string = ''
    found_entries = None

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['name', 'common_name',])
        all_entries = TaxonomySpecies.objects.filter(entry_query).order_by('name')

    paginator = Paginator(all_entries, 10)
    page = request.GET.get('page')
    try:
        found_entries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        found_entries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        found_entries = paginator.page(paginator.num_pages)

    #return render_to_response('browsing/search.html', { 'query_string': query_string, 'found_entries': found_entries }, RequestContext(request))
    return render_to_response('browsing/search.html', locals(), RequestContext(request))

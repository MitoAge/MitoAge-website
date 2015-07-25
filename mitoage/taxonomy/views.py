from abc import abstractmethod
import csv
from itertools import chain

from django.core import urlresolvers
from django.core.context_processors import request
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext, Context
from django.utils.text import slugify
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView

from mitoage.analysis.models import MitoAgeEntry, BaseComposition, CodonUsage, \
    BaseCompositionStats
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
    def __init__(self, name, named_url, arguments):
        self.name = name
        if arguments:
            self.url = reverse_lazy(named_url, args=arguments)
        else:
            self.url = reverse_lazy(named_url)


class BrowseAllClassesList(ListView):
    model = TaxonomyClass
    template_name = "browsing/taxonomy_class_list.html"
    paginate_by = 45
    
    def get_context_data(self, **kwargs):
        context = super(BrowseAllClassesList, self).get_context_data(**kwargs)
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "", None),]
        context['number_of_species'] = TaxonomySpecies.objects.all().count()
        return context


class TaxonomyClassDetail(SingleObjectMixin, ListView):
    template_name = "browsing/taxonomy_class_detail.html"
    model = TaxonomyClass
    paginate_by = 15

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
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=TaxonomyOrder.objects.all())
        return super(TaxonomyOrderDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaxonomyOrderDetail, self).get_context_data(**kwargs)
        context['taxonomy_order'] = self.object
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.taxonomy_class.name, "browse_class", [self.object.taxonomy_class.pk]),
                                  Breadcrumb(self.object.name, "", None),]
        return context

    def get_queryset(self):
        return self.object.taxonomy_families.all()

class TaxonomyFamilyDetail(SingleObjectMixin, ListView):
    template_name = "browsing/taxonomy_family_detail.html"
    model = TaxonomyFamily
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=TaxonomyFamily.objects.all())
        return super(TaxonomyFamilyDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TaxonomyFamilyDetail, self).get_context_data(**kwargs)
        context['taxonomy_family'] = self.object
        context['breadcrumbs'] = [Breadcrumb("All taxonomic classes", "browse_taxonomy", None), 
                                  Breadcrumb(self.object.taxonomy_order.taxonomy_class.name, "browse_class", [self.object.taxonomy_order.taxonomy_class.pk]),
                                  Breadcrumb(self.object.taxonomy_order.name, "browse_order", [self.object.taxonomy_order.pk]),
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
                                  Breadcrumb(self.object.taxonomy_family.taxonomy_order.taxonomy_class.name, "browse_class", [self.object.taxonomy_family.taxonomy_order.taxonomy_class.pk]),
                                  Breadcrumb(self.object.taxonomy_family.taxonomy_order.name, "browse_order", [self.object.taxonomy_family.taxonomy_order.pk]),
                                  Breadcrumb(self.object.taxonomy_family.name, "browse_family", [self.object.taxonomy_family.pk]),
                                  Breadcrumb(self.object.name, "", None),]
        context['base_compositions'] = self.get_base_compositions(self.object)
        context['general_sections'] = ["total_mtDNA", "total_pc_mtDNA", "d_loop_mtDNA", "total_tRNA_mtDNA", "total_rRNA_mtDNA", "rRNA_12S", "rRNA_16S"]
        context['gene_sections'] = ['atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6']
        context['codon_usages'] = self.get_codon_usages(self.object)
        context['codon_usage_sections'] = ['atp6', 'atp8', 'cox1', 'cox2', 'cox3', 'cytb', 'nd1', 'nd2', 'nd3', 'nd4', 'nd4l', 'nd5', 'nd6', 'total_pc_mtDNA']
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


def browse_all_genes(request):
    breadcrumbs = [Breadcrumb("All genes", "", None),]
    return render_to_response('browsing/browse_genes.html', locals(), RequestContext(request))

class StatsBrowsing(SingleObjectMixin, ListView):
    template_name = "browsing/stats_browsing.html"
    paginate_by = 15
    object = None
    taxon = None
    gene=None
    
    def get(self, request, *args, **kwargs):
        
        # if we want data only for a gene we take it from get
        if 'gene' in self.kwargs:
            self.gene = self.kwargs['gene']
        
        if ('taxon' in self.kwargs) and ('pk' in self.kwargs) :
            # we are working only with a subgroup of species
            self.taxon = self.kwargs['taxon']   #keeping it for later too
            model = {'family':TaxonomyFamily, 'order':TaxonomyOrder, 'class':TaxonomyClass}.get(self.taxon, None)
            
            if model:
                self.object = self.get_object(queryset=model.objects.all())    #hopefully pk will work
                return super(StatsBrowsing, self).get(request, *args, **kwargs)
            
            # silent fail - will return all species
        else:
            # we don't have a taxon and a pk because we want to work on all the species
            self.object = None
        return super(StatsBrowsing, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StatsBrowsing, self).get_context_data(**kwargs)
        
        if self.object:
            # we are working only with a subgroup of species
            context['title'] = "Stats %sfor %s <i>%s</i>" % ("of %s " % self.gene.upper() if self.gene else "", self.taxon, self.object.name)
            context['taxon'] = self.taxon
            context['subtaxon'] = {'family':'species', 'order':'family', 'class':'order'}.get(self.taxon, None)
            context['taxonomy_url'] = urlresolvers.reverse("browse_%s" % self.taxon, args=(self.object.pk,))
        else:
            # we don't have a taxon and a pk because we want to work on all the species
            context['title'] = "Stats %sfor all MitoAge species" % "of %s " % self.gene.upper() if self.gene else ""
            #context['taxon'] = self.taxon
            context['subtaxon'] = 'class'
            context['taxonomy_url'] = urlresolvers.reverse("browse_taxonomy")
        context['breadcrumbs'] = self.get_breadcrumbs()

        # get species and compute stats, according to gene/or not
        context['species'] = self.get_species()
        context['gene'] = self.gene
        if self.gene:
            context['stats'] = [ BaseCompositionStats(context['species'], self.gene, self.taxon, self.object) ]
        else:
            context['stats'] = [ BaseCompositionStats(context['species'], section, self.taxon, self.object) for section in BaseComposition.get_bc_sections() ]
        
        return context

    def get_queryset(self):
        if self.object:
            # if we are seeing stats for a family, we shouldn't browse futher to species - no point
            if self.taxon=='family':
                return self.object.taxonomy_species.all()
            elif self.taxon=='order':
                return self.object.taxonomy_families.all()
            elif self.taxon=='class':
                return self.object.taxonomy_orders.all()
        # if we are seeing stats for all species, browsing should show all classes
        return TaxonomyClass.objects.all()

    def get_breadcrumbs(self):
        breadcrumbs = []
        if self.gene:
            breadcrumbs.append( Breadcrumb("All genes", "browse_genes", None) )
            breadcrumbs.append( Breadcrumb("Gene %s (all species)" % self.gene.upper(), "stats", [self.gene]) )
            if self.taxon=='class':
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
            if self.taxon=='order':
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_class.name, "stats", [self.object.taxonomy_class.pk, 'class', self.gene]) )
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
            if self.taxon=='family':
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_order.taxonomy_class.name, "stats", [self.object.taxonomy_order.taxonomy_class.pk, 'class', self.gene]) )
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_order.name, "stats", [self.object.taxonomy_order.pk, 'order', self.gene]) )
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
             
        else:
            breadcrumbs.append( Breadcrumb("All species", "stats", None) ) 
            if self.taxon=='class':
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
            if self.taxon=='order':
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_class.name, "stats", [self.object.taxonomy_class.pk, 'class']) )
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
            if self.taxon=='family':
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_order.taxonomy_class.name, "stats", [self.object.taxonomy_order.taxonomy_class.pk, 'class']) )
                breadcrumbs.append( Breadcrumb(self.object.taxonomy_order.name, "stats", [self.object.taxonomy_order.pk, 'order']) )
                breadcrumbs.append( Breadcrumb(self.object.name, "stats", None) )
        return breadcrumbs

    def get_species(self):
        if self.object:
            if self.taxon == 'family':
                return self.object.taxonomy_species.all()
            if self.taxon == 'order':
                return TaxonomySpecies.objects.filter(taxonomy_family__taxonomy_order = self.object)
            if self.taxon == 'class':
                return TaxonomySpecies.objects.filter(taxonomy_family__taxonomy_order__taxonomy_class = self.object)
        return TaxonomySpecies.objects.all()


class CSVResponseMixin(object):
    """A generic mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request."""
    
    def get(self, request, *args, **kwargs):
        self.response_to_csv = self.respond_to_csv()
        return super(CSVResponseMixin, self).get(request, *args, **kwargs)
        
    def render_to_response(self, context, **response_kwargs):
        """ Creates a CSV response if requested, otherwise returns the default
        template response. """
        if self.response_to_csv:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s.csv"' % context['filename']

            csv_data = self.get_csv_data()
            t = self.get_csv_template() 

            c = Context({ 'data': csv_data, })
            response.write(t.render(c))
            return response
        # Business as usual otherwise
        else:
            return super(CSVResponseMixin, self).render_to_response(context, **response_kwargs)

    @abstractmethod
    def respond_to_csv(self):
        return False

    @abstractmethod
    def get_csv_template(self):
        return None
        
    @abstractmethod
    def get_csv_data(self, writer):
        return (
            ('Please', 're-write', 'this', 'method'),
            ('Please', 're-write', 'this', 'method'),
        )


class ExportTable(CSVResponseMixin, SingleObjectMixin, ListView):
    template_name = "browsing/export_data.html"
    paginate_by = 40
    object = None
    taxon = None
    section = None
    no_of_species = None

    def respond_to_csv(self):
        if 'export' in self.kwargs:
            if self.kwargs['export']=='csv':
                return True
        return False

    def get_csv_template(self):
        return loader.get_template("csv/export_data.txt")

    def get_csv_data(self):
        species = self.get_queryset()
        return [(s, self.section) for s in species]
        """
        return (
            ('Please', 're-write', 'this', 'method'),
            ('Please', 're-write', 'this', 'method'),
        )"""
    
    def get(self, request, *args, **kwargs):
        if 'section' in self.kwargs:
            self.section = self.kwargs['section']
        
        if ('taxon' in self.kwargs) and ('pk' in self.kwargs) :
            self.taxon = self.kwargs['taxon']   #keeping it for later too
            model = {'family':TaxonomyFamily, 'order':TaxonomyOrder, 'class':TaxonomyClass}.get(self.taxon, None)
            if model:
                self.object = self.get_object(queryset=model.objects.all())
                return super(ExportTable, self).get(request, *args, **kwargs)
            # silent fail - will return all species
        else:
            # we don't have a taxon and a pk because we want to work on all the species
            self.object = None
        return super(ExportTable, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExportTable, self).get_context_data(**kwargs)
        context['section'] = self.section
        context['taxon'] = self.taxon
        context['no_of_species'] = self.no_of_species
        context['other_sections'] = BaseComposition.get_bc_sections()
        context['other_sections'].remove(self.section)
        if self.object:
            # we are working only with a subgroup of species
            context['title'] = "Export data %sfor %s <i>%s</i>" % ("of %s " % BaseComposition.total_title_lower(BaseComposition.get_nice_title(self.section)) if self.section else "", self.taxon, self.object.name)
            context['filename'] = slugify("%s-%s-%s" % (self.section, self.taxon, self.object.name))
            context['taxon'] = self.taxon
        else:
            # we don't have a taxon and a pk because we want to work on all the species
            context['title'] = "Export data %sfor all MitoAge species" % "of %s " % BaseComposition.total_title_lower(BaseComposition.get_nice_title(self.section)) if self.section else ""
            context['filename'] = slugify("%s-all-species" % self.section)

        return context

    def get_queryset(self):
        if self.object:
            if self.taxon == 'family':
                mitoage_entries = MitoAgeEntry.objects.filter(species__taxonomy_family = self.object)
            if self.taxon == 'order':
                mitoage_entries = MitoAgeEntry.objects.filter(species__taxonomy_family__taxonomy_order = self.object)
            if self.taxon == 'class':
                mitoage_entries = MitoAgeEntry.objects.filter(species__taxonomy_family__taxonomy_order__taxonomy_class = self.object)
        else:
            mitoage_entries = MitoAgeEntry.objects.all()

        section_translation = {'total_mtDNA':'total_mtDNA', 'total_pc_mtDNA':'total_mtDNA_pc', 'd_loop_mtDNA':'d_loop', 
                               'total_tRNA_mtDNA':'total_tRNA', 'total_rRNA_mtDNA':'total_rRNA', 'atp6':'atp6', 'atp8':'atp8', 
                               'cox1':'cox1', 'cox2':'cox2', 'cox3':'cox3', 'cytb':'cytb', 'nd1':'nd1', 'nd2':'nd2', 'nd3':'nd3', 
                               'nd4':'nd4', 'nd4l':'nd4l', 'nd5':'nd5', 'nd6':'nd6', 'rRNA_12S':'rRNA_12S', 'rRNA_16S':'rRNA_16S'}.get(self.section, 'total_mtDNA')
        kwargs1 = { ('bc_%s_size__isnull' % section_translation): 'True', }
        kwargs2 = { ('bc_%s_size__exact' % section_translation): '0', }
        mitoage_entries = mitoage_entries.exclude(**kwargs1).exclude(**kwargs2).order_by('species__name')
        species = [ e.species for e in mitoage_entries ]
        self.no_of_species = len(species)
        return species


def search(request):
    query_string = ''
    found_entries = None

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['name', 'common_name',])
        found_species = TaxonomySpecies.objects.filter(entry_query).order_by('name')

        entry_query = get_query(query_string, ['name',])
        found_families = TaxonomyFamily.objects.filter(entry_query).order_by('name')
        found_orders = TaxonomyOrder.objects.filter(entry_query).order_by('name')
        found_classes = TaxonomyClass.objects.filter(entry_query).order_by('name')
        
        all_entries = list(chain(found_classes, found_orders, found_families, found_species))

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

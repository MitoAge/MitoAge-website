from django.core.urlresolvers import reverse_lazy
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView

from mitoage.taxonomy.models import TaxonomyClass, TaxonomyOrder, TaxonomyFamily, \
    TaxonomySpecies


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
        return context

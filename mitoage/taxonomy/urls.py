#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from mitoage.taxonomy.views import BrowseAllClassesList, TaxonomyClassDetail, \
    TaxonomyOrderDetail, TaxonomyFamilyDetail, TaxonomySpeciesDetail, search


urlpatterns = patterns('mitoage.taxonomy.views',

    url(r'^browse/taxonomy/$', BrowseAllClassesList.as_view(), name='browse_taxonomy'),
    url(r'^browse/(?P<pk>[0-9]+)/class/$', TaxonomyClassDetail.as_view(), name='browse_class'),
    url(r'^browse/(?P<pk>[0-9]+)/order/$', TaxonomyOrderDetail.as_view(), name='browse_order'),
    url(r'^browse/(?P<pk>[0-9]+)/family/$', TaxonomyFamilyDetail.as_view(), name='browse_family'),
    url(r'^view/(?P<pk>[0-9]+)/species/$', TaxonomySpeciesDetail.as_view(), name='view_species'),

    url(r'^browse/genes/$', TemplateView.as_view(template_name="static_pages/home.html"), name='browse_genes'),
    url(r'^view/(?P<gene>[\w]+)/gene/$', TemplateView.as_view(template_name="static_pages/home.html"), name='view_gene'),
    
    url(r'^search/$', search, name='search'),
    
)

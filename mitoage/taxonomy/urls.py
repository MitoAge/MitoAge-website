from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from mitoage.taxonomy.views import BrowseAllClassesList, TaxonomyClassDetail, \
    TaxonomyOrderDetail, TaxonomyFamilyDetail, TaxonomySpeciesDetail, search, \
    StatsBrowsing, browse_all_genes


urlpatterns = patterns('mitoage.taxonomy.views',

    url(r'^browse/taxonomy/$', BrowseAllClassesList.as_view(), name='browse_taxonomy'),
    url(r'^browse/(?P<pk>[0-9]+)/class/$', TaxonomyClassDetail.as_view(), name='browse_class'),
    url(r'^browse/(?P<pk>[0-9]+)/order/$', TaxonomyOrderDetail.as_view(), name='browse_order'),
    url(r'^browse/(?P<pk>[0-9]+)/family/$', TaxonomyFamilyDetail.as_view(), name='browse_family'),
    url(r'^view/(?P<pk>[0-9]+)/species/$', TaxonomySpeciesDetail.as_view(), name='view_species'),

    url(r'^browse/genes/$', browse_all_genes, name='browse_genes'),
    url(r'^stats-for/all-species/$', StatsBrowsing.as_view(), name='stats'),
    url(r'^stats-for/(?P<gene>[\w]+)/gene/$', StatsBrowsing.as_view(), name='stats'),
    url(r'^stats-for/(?P<pk>[0-9]+)/(?P<taxon>[\w]+)/$', StatsBrowsing.as_view(), name='stats'),
    url(r'^stats-for/(?P<pk>[0-9]+)/(?P<taxon>[\w]+)/for-gene/(?P<gene>[\w]+)/$', StatsBrowsing.as_view(), name='stats'),

    #url(r'^view/(?P<gene>[\w]+)/gene-stats/$', TemplateView.as_view(template_name="static_pages/home.html"), name='all_gene_stats'),
    #url(r'^view/(?P<gene>[\w]+)/gene-stats-in-the/(?P<pk>[0-9]+)/(?P<taxon>[\w]+)/$', TemplateView.as_view(template_name="static_pages/home.html"), name='gene_stats_taxon'),

    #url(r'^view/(?P<gene>[\w]+)/gene-stats-in-the/(?P<pk>[0-9]+)/class/$', TaxonomyClassDetail.as_view(), name='browse_class'),
    #url(r'^view/(?P<gene>[\w]+)/gene-stats-in-the/(?P<pk>[0-9]+)/order/$', TaxonomyOrderDetail.as_view(), name='browse_order'),
    #url(r'^view/(?P<gene>[\w]+)/gene-stats-in-the/(?P<pk>[0-9]+)/family/$', TaxonomyFamilyDetail.as_view(), name='browse_family'),
    
    url(r'^search/$', search, name='search'),
    
)

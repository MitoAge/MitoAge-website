from django.conf.urls import patterns, url

from mitoage.taxonomy.views import BrowseAllClassesList, TaxonomyClassDetail, \
    TaxonomyOrderDetail, TaxonomyFamilyDetail, TaxonomySpeciesDetail, search, \
    StatsBrowsing, browse_all_genes, ExportTable


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

    url(r'^export-section/(?P<section>[\w]+)/for-all-species/$', ExportTable.as_view(), name='export-table'),
    url(r'^export-section/(?P<section>[\w]+)/(?P<export>[\w]+)/for-all-species/$', ExportTable.as_view(), name='export-table'),
    url(r'^export-section/(?P<section>[\w]+)/for/(?P<pk>[0-9]+)/(?P<taxon>[\w]+)/$', ExportTable.as_view(), name='export-table'),
    url(r'^export-section/(?P<section>[\w]+)/(?P<export>[\w]+)/for/(?P<pk>[0-9]+)/(?P<taxon>[\w]+)/$', ExportTable.as_view(), name='export-table'),

    url(r'^search/$', search, name='search'),
    
)

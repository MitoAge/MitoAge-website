from django.conf.urls import patterns, url

from mitoage.analysis.views import statistics, compare, add_to_compare_cart, \
    delete_from_compare_cart


urlpatterns = patterns('mitoage.analysis.views',

    url(r'^statistics/$', statistics, name='statistics'),
    
    url(r'^compare/$', compare, name='compare'),
    url(r'^add_to_compare_cart/(?P<pk>[0-9]+)/$', add_to_compare_cart, name='add_to_compare_cart'),
    url(r'^delete_from_compare_cart/(?P<pk>[0-9]+)/$', delete_from_compare_cart, name='delete_from_compare_cart'),
)

from django.conf.urls import patterns, url

from mitoage.analysis.views import statistics


urlpatterns = patterns('mitoage.analysis.views',

    url(r'^statistics/$', statistics, name='statistics'),
    
)

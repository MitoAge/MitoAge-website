#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView


urlpatterns = patterns('mitoage.taxonomy.views',
    url(r'^taxonomy/browser/$', TemplateView.as_view(template_name="static_pages/home.html"), name='browse_taxonomy'),
)

"""
    url(r'^taxonomy/browse/$', 'browse_taxonomy', name='browse_taxonomy'),
    url(r'^taxonomy/browse/$', 'browse_taxonomy', name='browse_taxonomy'),
    url(r'^taxonomy/browse/$', 'browse_taxonomy', name='browse_taxonomy'),
    url(r'^user/(?P<user_short_url>[\w]+)/profile/$', 'trust_me.user_management.views.user_profile', name='user_profile'),
"""

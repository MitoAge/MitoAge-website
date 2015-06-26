from django.conf.urls import patterns, include, url
from django.contrib import admin
from mitoage import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mitoage.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Our custom made packages == virtual character
    url(r'', include('mitoage.static_pages.urls')),
    url(r'', include('mitoage.taxonomy.urls')),


    # admin
    url(r'^admin/', include(admin.site.urls)),
    
    # Static and media page serving
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT} ),

)

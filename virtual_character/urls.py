from django.conf.urls import patterns, include, url
from django.contrib import admin
from virtual_character import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'virtual_character.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Our custom made packages == virtual character
    #url(r'', include('virtual_character.website.urls')),
    #url(r'', include('virtual_character.debugging.urls')),


    # admin
    url(r'^admin/', include(admin.site.urls)),
    
    # Static and media page serving
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT} ),

)

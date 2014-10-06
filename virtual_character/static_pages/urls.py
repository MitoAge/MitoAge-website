from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView

urlpatterns = patterns('virtual_character.static_pages.views',

    url(r'^$',  RedirectView.as_view(url='about_us'), name='home'),
    url(r'^test_page/$', TemplateView.as_view(template_name="static_pages/test_page.html"), name='test_page'),
    url(r'^about_us/$', TemplateView.as_view(template_name="static_pages/about_us.html"), name='about_us'),
)

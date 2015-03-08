from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView

urlpatterns = patterns('mitoage.static_pages.views',

    url(r'^$', TemplateView.as_view(template_name="static_pages/home.html"), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name="static_pages/about.html"), name='about'),
    url(r'^user_guide/$', TemplateView.as_view(template_name="static_pages/user_guide.html"), name='user_guide'),
    url(r'^glossary/$', TemplateView.as_view(template_name="static_pages/glossary.html"), name='glossary'),
    url(r'^methods/$', TemplateView.as_view(template_name="static_pages/methods.html"), name='methods'),
    url(r'^download/$', TemplateView.as_view(template_name="static_pages/download.html"), name='download'),
    url(r'^news/$', TemplateView.as_view(template_name="static_pages/news.html"), name='news'),
    url(r'^terms/$', TemplateView.as_view(template_name="static_pages/terms.html"), name='terms'),

    #url(r'^$',  RedirectView.as_view(url='about_us'), name='home'),
)

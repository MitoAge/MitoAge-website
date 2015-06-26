from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

class SpeciesView(object):
    #queryset = Gallery.objects.filter(is_public=True)
    pass

class SpeciesListView(SpeciesView, ListView):
    paginate_by = 20

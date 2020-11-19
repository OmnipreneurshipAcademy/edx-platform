"""
All views for Bootcamps application.
"""
from django.views.generic import ListView, DetailView

from .models import Bootcamp


class BootcampsListView(ListView):
    """
    Generic view to display the list of all Bootcamps
    """
    model = Bootcamp
    context_object_name = "bootcamps"
    template_name = 'adg/lms/bootcamps/list.html'


class BootcampDetailView(DetailView):
    """
    Generic view to display the detail page of a single Bootcamp
    """
    model = Bootcamp
    context_object_name = "bootcamp"
    template_name = 'adg/lms/bootcamps/detail.html'

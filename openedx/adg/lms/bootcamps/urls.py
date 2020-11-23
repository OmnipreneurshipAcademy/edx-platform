"""
All urls for Bootcamps application.
"""
from django.urls import path

from .views import BootcampDetailView, BootcampsListView

app_name = 'bootcamps'
urlpatterns = [
    path('', BootcampsListView.as_view(), name='bootcamp_list'),
    path('<int:pk>/', BootcampDetailView.as_view(), name='bootcamp_detail'),
]

"""
Urls for `admin_dashboard.applications` app
"""
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_summary.html')
    ),
    path(
        'list/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_list.html')
    ),
    path(
        '<int:application_id>/review/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/application_review.html')
    ),
]

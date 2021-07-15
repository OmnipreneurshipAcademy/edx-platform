"""
URLs for `admin_dashboard.applications` app
"""
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_summary.html')
    ),
    path(
        'list/open/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_list_open.html')
    ),
    path(
        'list/waitlisted/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_list_waitlisted.html')
    ),
    path(
        'list/accepted/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/applications_list_accepted.html')
    ),
    path(
        '<int:application_id>/review/',
        TemplateView.as_view(template_name='adg/admin_dashboard/applications/application_review.html')
    ),
]

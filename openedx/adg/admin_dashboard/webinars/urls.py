"""
URLs for `admin_dashboard.webinars` app
"""
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='adg/admin_dashboard/webinars/webinars_list.html')
    ),
    path(
        'add/',
        TemplateView.as_view(template_name='adg/admin_dashboard/webinars/add_webinar.html')
    ),
    path(
        '<int:webinar_id>/update/',
        TemplateView.as_view(template_name='adg/admin_dashboard/webinars/update_webinar.html')
    ),
]

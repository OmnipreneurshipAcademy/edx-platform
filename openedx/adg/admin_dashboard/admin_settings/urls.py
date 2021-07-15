"""
URLs for `admin_settings` app
"""
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='adg/admin_dashboard/admin_settings/settings.html')
    ),
    path(
        'admin_accounts/',
        TemplateView.as_view(template_name='adg/admin_dashboard/admin_settings/accounts.html')
    ),
]

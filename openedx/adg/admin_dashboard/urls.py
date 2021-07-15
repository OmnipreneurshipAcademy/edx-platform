"""
URLs for `admin_dashboard`
"""
from django.urls import include, path

urlpatterns = [
    path('applications/', include('openedx.adg.admin_dashboard.applications.urls')),
    path('performance/', include('openedx.adg.admin_dashboard.performance.urls')),
    path('settings/', include('openedx.adg.admin_dashboard.admin_settings.urls')),
    path('webinars/', include('openedx.adg.admin_dashboard.webinars.urls')),
]

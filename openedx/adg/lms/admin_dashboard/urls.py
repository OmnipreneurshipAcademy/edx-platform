"""
Urls for `admin_dashboard`
"""
from django.urls import include, path

urlpatterns = [
    path('settings/', include('openedx.adg.lms.admin_dashboard.admin_settings.urls')),
    path('performance/', include('openedx.adg.lms.admin_dashboard.performance.urls')),
    path('webinars/', include('openedx.adg.lms.admin_dashboard.webinars.urls')),
    path('applications/', include('openedx.adg.lms.admin_dashboard.applications.urls')),
]

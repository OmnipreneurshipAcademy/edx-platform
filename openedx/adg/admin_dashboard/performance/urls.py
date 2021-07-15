"""
Urls for `performance` app
"""
from django.conf import settings
from django.urls import path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='adg/admin_dashboard/performance/performance_tracking.html')
    ),
    re_path(
        r'{}/grades/'.format(settings.COURSE_KEY_PATTERN),
        TemplateView.as_view(template_name='adg/admin_dashboard/performance/course_performance.html')
    ),
]

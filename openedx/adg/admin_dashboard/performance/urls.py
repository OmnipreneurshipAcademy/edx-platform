"""
URLs for `performance` app
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
        rf'{settings.COURSE_KEY_PATTERN}/grades/',
        TemplateView.as_view(template_name='adg/admin_dashboard/performance/course_grade.html')
    ),
]

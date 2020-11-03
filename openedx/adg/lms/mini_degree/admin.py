"""
Admin registration for MiniDegree Models
"""
from django.contrib import admin

from .models import MiniDegree


@admin.register(MiniDegree)
class MiniDegreeAdmin(admin.ModelAdmin):
    """
    Django admin customizations for MiniDegree model
    """

    list_display = ('title', 'subtitle')
    search_fields = ('title', 'subtitle')

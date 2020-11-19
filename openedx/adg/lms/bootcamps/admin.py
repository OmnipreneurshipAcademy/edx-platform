"""
Registering admin models for Bootcamps application.
"""
from django.contrib import admin

from .models import Bootcamp


@admin.register(Bootcamp)
class BootcampAdmin(admin.ModelAdmin):
    """
    Django admin class for Bootcamp
    """
    fields = ('title', 'courses',)
    list_display = ('title',)

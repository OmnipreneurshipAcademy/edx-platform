"""
Registering models for applications app.
"""
from django.contrib import admin
from .models import ApplicationHub, BusinessLine, Education, UserApplication, WorkExperience, Book, AdminNote
from rules.contrib.admin import ObjectPermissionsModelAdmin


@admin.register(Book)
class BookAdmin(ObjectPermissionsModelAdmin):
    """
    Django admin class for BusinessLine
    """

    pass


@admin.register(ApplicationHub)
class ApplicationHubAdmin(admin.ModelAdmin):
    """
    Django admin class for ApplicationHub
    """
    fields = ('user', 'is_prerequisite_courses_passed', 'is_application_submitted',)
    list_display = (
        'id', 'user', 'is_prerequisite_courses_passed', 'is_application_submitted',
    )
    raw_id_fields = ('user',)


class EducationAdmin(admin.StackedInline):
    """
    Django admin class for Education
    """
    model = Education


class WorkExperienceAdmin(admin.StackedInline):
    """
    Django admin class for WorkExperience
    """
    model = WorkExperience


class AdminNoteAdmin(admin.StackedInline):
    """
    Django admin class for BusinessLine
    """
    model = AdminNote


class BusinessLineAdmin(admin.StackedInline):
    """
    Django admin class for BusinessLine
    """
    model = BusinessLine


@admin.register(UserApplication)
class UserApplicationAdmin(admin.ModelAdmin):
    """
    Django admin class for UserApplication
    """
    list_display = ('id', 'user_email', 'business_line',)

    def user_email(self, obj):
        return obj.user.email

    def get_queryset(self, request):
        qs = super(UserApplicationAdmin, self).get_queryset(request)

        from .rules import is_bu_admin
        if request.user.is_superuser or is_bu_admin(request.user):
            return qs

        return qs.filter(business_line__group__in=request.user.groups.all())

    inlines = [EducationAdmin, WorkExperienceAdmin, AdminNoteAdmin, ]

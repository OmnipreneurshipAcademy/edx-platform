"""
Registering models with for applications app.
"""
from django.contrib import admin

from .models import ApplicationHub, Education, UserApplication, WorkExperience


@admin.register(ApplicationHub)
class ApplicationHubAdmin(admin.ModelAdmin):
    """
    Django admin class for ApplicationHub
    """
    fields = ('user', 'is_prerequisite_courses_passed', 'is_application_submitted', 'is_assessment_completed',)
    list_display = (
        'id', 'user', 'is_prerequisite_courses_passed', 'is_application_submitted', 'is_assessment_completed'
    )
    raw_id_fields = ('user',)


@admin.register(UserApplication)
class UserApplicationAdmin(admin.ModelAdmin):
    """
    Django admin class for UserApplication
    """
    fields = ('user', 'city', 'organization', 'linkedin_url', 'resume', 'cover_letter_file', 'cover_letter',)
    list_display = ('id', 'user_email', 'city',)
    list_filter = ('city', 'user__profile__country')
    raw_id_fields = ('user', )

    def user_email(self, obj):
        return obj.user.email


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """
    Django admin class for Education
    """
    fields = (
        'name_of_school', 'degree', 'ares_of_study', 'date_started_month', 'date_started_year', 'date_completed_month',
        'date_completed_year', 'is_in_progress', 'user_application',
    )
    list_display = ('id', 'name_of_school', 'degree', 'ares_of_study', 'user_application',)
    list_filter = ('degree', 'ares_of_study',)
    search_fields = ('name_of_school', 'degree',)


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    """
    Django admin class for WorkExperience
    """
    fields = (
        'name_of_organization', 'job_position_title', 'date_started_month', 'date_started_year', 'date_completed_month',
        'date_completed_year', 'is_current_position', 'job_responsibilities', 'user_application'
    )
    list_display = ('id', 'name_of_organization', 'job_position_title', 'user_application',)
    list_filter = ('name_of_organization', 'job_position_title',)
    search_fields = ('name_of_organization', 'job_position_title',)

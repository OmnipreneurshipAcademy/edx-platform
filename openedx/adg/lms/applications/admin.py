"""
Registering models for applications app.
"""
from django.contrib import admin

from .models import (
    ApplicationHub,
    BusinessLine,
    Education,
    PrerequisiteCourse,
    PrerequisiteCourseGroup,
    UserApplication,
    WorkExperience
)


@admin.register(ApplicationHub)
class ApplicationHubAdmin(admin.ModelAdmin):
    """
    Django admin class for ApplicationHub
    """
    fields = (
        'user', 'is_prerequisite_courses_passed', 'is_written_application_completed', 'is_application_submitted',
        'submission_date'
    )
    list_display = (
        'id', 'user', 'is_prerequisite_courses_passed', 'is_written_application_completed', 'is_application_submitted',
        'submission_date'
    )
    raw_id_fields = ('user',)


@admin.register(UserApplication)
class UserApplicationAdmin(admin.ModelAdmin):
    """
    Django admin class for UserApplication
    """
    list_display = ('id', 'user_email', 'business_line',)
    list_filter = ('business_line',)
    raw_id_fields = ('user',)

    def user_email(self, obj):
        return obj.user.email


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """
    Django admin class for Education
    """
    fields = (
        'name_of_school', 'degree', 'area_of_study', 'date_started_month', 'date_started_year', 'date_completed_month',
        'date_completed_year', 'is_in_progress', 'user_application',
    )
    list_display = ('id', 'name_of_school', 'degree', 'area_of_study', 'user_application',)
    list_filter = ('degree', 'area_of_study',)
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


@admin.register(BusinessLine)
class BusinessLineAdmin(admin.ModelAdmin):
    """
    Django admin class for BusinessLine
    """
    fields = ('title', 'logo', 'description',)
    list_display = ('id', 'title', 'logo', 'description',)
    list_filter = ('title',)
    search_fields = ('title',)


class PrerequisiteCourseAdmin(admin.TabularInline):
    model = PrerequisiteCourse


@admin.register(PrerequisiteCourseGroup)
class PrerequisiteCourseGroupAdmin(admin.ModelAdmin):
    inlines = [PrerequisiteCourseAdmin, ]
    list_display = ('name', 'prereq_course_count', 'open_prereq_courses_count',)

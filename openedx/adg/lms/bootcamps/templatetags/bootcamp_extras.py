"""
Custom template tags for Bootcamps application.
"""
from django import template
from django.contrib.auth.models import User
from openedx.adg.lms.utils.adg_utils import is_user_failed_in_course

from .constants import (
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED
)
from .helpers import is_user_enrolled_in_course

register = template.Library()


@register.filter(name='progress_display')
def get_course_progress_for_user(username, course_id):
    """
    Checks the course progress for a particular user and returns the progress in str
    Args:
        username: str
        course_id: CourseLocator object
    Returns:
        NOT_STARTED i.e "Not Started" if enrollment not found
        IN_PROGRESS i.e "In Progress" if enrollment found but course is not passed yet by the user
        COMPLETED i.e "Completed" if enrollment found and the course is also passed
    """
    if is_user_enrolled_in_course(username, course_id):
        student = User.objects.get(username=username)
        if is_user_failed_in_course(student, course_id):
            return IN_PROGRESS
        return COMPLETED
    else:
        return NOT_STARTED

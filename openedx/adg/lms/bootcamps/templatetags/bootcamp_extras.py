"""
Custom template tags for Bootcamps application.
"""
from django import template

from .constants import (
    NOT_STARTED,
    COMPLETED,
    IN_PROGRESS,
    MAP_PROGRESS_INTEGER_TO_STRING
)
from .helpers import get_course_progress_for_user

register = template.Library()


@register.filter(name='progress_display')
def course_progress(username, course_id):
    """
    Displays the progress of the course in str
    Args:
        username: str
        course_id: CourseLocator object
    Returns:
        Returns the progress in str
        e.g if status is 0, "Not Started" is returned
    """
    progress_status = get_course_progress_for_user(username, course_id)
    if progress_status == NOT_STARTED:
        return MAP_PROGRESS_INTEGER_TO_STRING[NOT_STARTED]
    elif progress_status == IN_PROGRESS:
        return MAP_PROGRESS_INTEGER_TO_STRING[IN_PROGRESS]
    elif progress_status == COMPLETED:
        return MAP_PROGRESS_INTEGER_TO_STRING[COMPLETED]
    else:
        return ""

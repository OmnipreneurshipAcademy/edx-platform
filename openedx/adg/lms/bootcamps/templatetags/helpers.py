"""
Helper/utility function for Bootcamps application's templatetags.
"""
from django.contrib.auth.models import User
from openedx.adg.lms.applications.management.commands.update_is_prerequisite_courses_passed import Command
from openedx.core.djangoapps.enrollments.api import get_enrollment

from .constants import (
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED
)


def is_user_enrolled_in_course(username, course_id):
    """
    Checks if the specified user is enrolled in a specific course
    Args:
        username: str
        course_id: CourseLocator object
    Returns:
        Boolean; returns True if the enrolled is found active otherwise returns False
    """
    enrollment = get_enrollment(username, str(course_id))
    if enrollment and enrollment.get("is_active"):
        return True
    return False


def get_course_progress_for_user(username, course_id):
    """
    Checks the course progress for a particular user
    Args:
        username: str
        course_id: CourseLocator object
    Returns:
        NOT_STARED i.e 0 if enrollment not found
        IN_PROGRESS i.e 1 if enrollment found but course is not passed yet by the user
        COMPLETED i.e 2 if enrollment found and the course is also passed
    """
    if is_user_enrolled_in_course(username, course_id):
        student = User.objects.get(username=username)
        user_status = Command()
        if user_status.is_user_failed_in_course(student, course_id):
            return IN_PROGRESS
        return COMPLETED
    else:
        return NOT_STARTED

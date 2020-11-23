"""
Helper/utility function for Bootcamps application's templatetags.
"""
from openedx.core.djangoapps.enrollments.api import get_enrollment


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
    if enrollment and enrollment.get('is_active'):
        return True
    return False

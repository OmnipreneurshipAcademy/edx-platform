"""
Utility functions for ADG applications
"""
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory


def is_user_failed_in_course(user, course_key):
    """
    Checks if user is failed in the given course
    Args:
        user: User object
        course_key: CourseLocator object
    Returns:
        boolean, True if the course is failed otherwise False
    """
    course_grade = CourseGradeFactory().read(user, course_key=course_key)
    return not (course_grade and course_grade.passed)

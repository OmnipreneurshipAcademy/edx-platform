"""
Factory for use in tests of update_is_prerequisite_courses_passed
management command
"""


from factory import DjangoModelFactory

from openedx.adg.common.course_meta.models import CourseMeta


class CourseMetaFactory(DjangoModelFactory):
    class Meta:
        model = CourseMeta
        django_get_or_create = ('course', 'is_prereq',)

    is_prereq = True

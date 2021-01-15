"""
All model factories for applications
"""
import factory

from openedx.adg.lms.applications.models import (
    ApplicationHub,
    BusinessLine,
    Education,
    PrerequisiteCourse,
    PrerequisiteCourseGroup,
    UserApplication,
    WorkExperience
)
from openedx.core.djangoapps.content.course_overviews.tests.factories import CourseOverviewFactory
from student.tests.factories import UserFactory


class BusinessLineFactory(factory.DjangoModelFactory):
    """
    Factory for BusinessLine model
    """

    class Meta:
        model = BusinessLine

    title = factory.Faker('word')
    description = factory.Faker('sentence')


class UserApplicationFactory(factory.DjangoModelFactory):
    """
    Factory for UserApplication model
    """

    class Meta:
        model = UserApplication

    user = factory.SubFactory(UserFactory)
    business_line = factory.SubFactory(BusinessLineFactory)
    organization = 'testOrganization'


class ApplicationHubFactory(factory.DjangoModelFactory):
    """
    Factory for ApplicationHub Model
    """

    class Meta:
        model = ApplicationHub
        django_get_or_create = ('user',)

    user = factory.SubFactory(UserFactory)


class EducationFactory(factory.DjangoModelFactory):
    """
    Factory for Education model
    """

    class Meta:
        model = Education

    user_application = factory.SubFactory(UserApplicationFactory)
    name_of_school = factory.Faker('word')
    degree = Education.BACHELOR_DEGREE
    area_of_study = factory.Faker('sentence')
    date_started_month = 1
    date_started_year = 2018
    date_completed_month = 1
    date_completed_year = 2020


class WorkExperienceFactory(factory.DjangoModelFactory):
    """
    Factory for Work experience model
    """

    class Meta:
        model = WorkExperience

    user_application = factory.SubFactory(UserApplicationFactory)
    name_of_organization = factory.Faker('word')
    job_position_title = factory.Faker('word')
    job_responsibilities = factory.Faker('sentence')
    date_started_month = 1
    date_started_year = 2018
    date_completed_month = 1
    date_completed_year = 2020


class PrerequisiteCourseGroupFactory(factory.DjangoModelFactory):
    """
    Factory for Work experience model
    """

    name = factory.Sequence(lambda n: 'Course group #%s' % n)

    class Meta:
        model = PrerequisiteCourseGroup


class PrerequisiteCourseFactory(factory.DjangoModelFactory):
    """
    Factory for Work experience model
    """

    course = factory.SubFactory(CourseOverviewFactory)
    prereq_course_group = factory.SubFactory(PrerequisiteCourseGroupFactory)

    class Meta:
        model = PrerequisiteCourse

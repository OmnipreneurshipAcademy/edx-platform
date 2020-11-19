"""
Tests for all the code in templatetags/bootcamp_extras.py in Bootcamps application.
"""
import mock

from openedx.adg.lms.bootcamps.templatetags.bootcamp_extras import course_progress
from openedx.adg.lms.bootcamps.templatetags.constants import (
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED,
    MAP_PROGRESS_INTEGER_TO_STRING
)
from openedx.core.djangoapps.content.course_overviews.tests.factories import CourseOverviewFactory
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class BootcampExtrasTestCases(ModuleStoreTestCase):
    """
    TestCase for the bootcamp_extras functions
    """
    USERNAME = "test"
    EMAIL = "test@example.com"
    PASSWORD = "edx"

    def setUp(self):
        super(BootcampExtrasTestCases, self).setUp()
        self.dummy_user = UserFactory(username=self.USERNAME, email=self.EMAIL, password=self.PASSWORD)
        self.dummy_course = CourseFactory.create(display_name='test course 1', run='Testing_course_1')
        self.course_overview = CourseOverviewFactory.create(id=self.dummy_course.id)

    def test_course_progress_tag(self):
        """
        Test the course progress tag function for all the possible situations i.e Not started, In Progress and
        Completed.
        """
        actual_progress_given = course_progress(self.dummy_user.username, self.course_overview.id)
        self.assertEqual(actual_progress_given, MAP_PROGRESS_INTEGER_TO_STRING[NOT_STARTED])

        CourseEnrollmentFactory.create(user=self.dummy_user, course_id=self.dummy_course.id)
        actual_progress_given = course_progress(self.dummy_user.username, self.course_overview.id)
        self.assertEqual(actual_progress_given, MAP_PROGRESS_INTEGER_TO_STRING[IN_PROGRESS])

        with mock.patch('openedx.adg.lms.bootcamps.templatetags.helpers.Command', autospec=True) as status_mock:
            status_mock.return_value.is_user_failed_in_course.return_value = False
            actual_progress_given = course_progress(self.dummy_user.username, self.course_overview.id)
        self.assertEqual(actual_progress_given, MAP_PROGRESS_INTEGER_TO_STRING[COMPLETED])

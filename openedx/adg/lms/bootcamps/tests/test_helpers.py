"""
Tests for all the code in templatetags/helpers.py Bootcamps application.
"""
import mock

from openedx.adg.lms.bootcamps.templatetags.constants import (
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED
)
from openedx.adg.lms.bootcamps.templatetags.helpers import (
    is_user_enrolled_in_course,
    get_course_progress_for_user,
)
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class HelpersTestCase(ModuleStoreTestCase):
    """
    TestCase class for the helpers.py functions
    """
    USERNAME = "test"
    EMAIL = "test@example.com"
    PASSWORD = "edx"

    def setUp(self):
        super(HelpersTestCase, self).setUp()
        self.user = UserFactory(username=self.USERNAME, email=self.EMAIL, password=self.PASSWORD)
        self.dummy_course = CourseFactory.create(display_name='test course 1', run='Testing_course_1')

    def test_is_user_enrolled_in_course(self):
        """
        Tests if the function correctly reports the enrollment status for a user-course pair.
        """
        self.assertFalse(is_user_enrolled_in_course(self.user.username, self.dummy_course.id))
        CourseEnrollmentFactory.create(user=self.user, course_id=self.dummy_course.id)
        self.assertTrue(is_user_enrolled_in_course(self.user.username, self.dummy_course.id))

    def test_get_course_progress_for_user(self):
        """
        Tests if the progress reported by the function is correct or not.
        """
        self.assertEqual(get_course_progress_for_user(self.user.username, self.dummy_course.id), NOT_STARTED)

        CourseEnrollmentFactory.create(user=self.user, course_id=self.dummy_course.id)
        self.assertEqual(get_course_progress_for_user(self.user.username, self.dummy_course.id), IN_PROGRESS)

        with mock.patch('openedx.adg.lms.bootcamps.templatetags.helpers.Command', autospec=True) as status_mock:
            status_mock.return_value.is_user_failed_in_course.return_value = False
            actual_progress_given = get_course_progress_for_user(self.user.username, self.dummy_course.id)
        self.assertEqual(actual_progress_given, COMPLETED)

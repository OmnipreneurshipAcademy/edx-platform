"""
Tests for all the template tags.
"""
import mock
from openedx.adg.lms.bootcamps.templatetags.bootcamp_extras import (
    get_course_progress_for_user,
)
from openedx.adg.lms.bootcamps.templatetags.constants import (
    NOT_STARTED,
    IN_PROGRESS,
    COMPLETED,
    USERNAME,
    EMAIL,
    PASSWORD
)
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class BootcampExtrasTestCase(ModuleStoreTestCase):
    """
    TestCase class for the template tag functions
    """

    def setUp(self):
        super(BootcampExtrasTestCase, self).setUp()
        self.user = UserFactory(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.dummy_course = CourseFactory.create(display_name='test course 1', run='Testing_course_1')

    def test_get_course_progress_for_user(self):
        """
        Tests if the progress reported by the function is correct or not.
        """
        self.assertEqual(get_course_progress_for_user(self.user.username, self.dummy_course.id), NOT_STARTED)

        CourseEnrollmentFactory.create(user=self.user, course_id=self.dummy_course.id)
        self.assertEqual(get_course_progress_for_user(self.user.username, self.dummy_course.id), IN_PROGRESS)

        with mock.patch('openedx.adg.lms.bootcamps.templatetags.bootcamp_extras.is_user_failed_in_course',
                        autospec=True) as status_mock:
            status_mock.return_value = False
            actual_progress_given = get_course_progress_for_user(self.user.username, self.dummy_course.id)
        self.assertEqual(actual_progress_given, COMPLETED)

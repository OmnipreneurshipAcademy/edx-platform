"""
Tests for all the template tags helpers.
"""
from openedx.adg.lms.bootcamps.templatetags.helpers import (
    is_user_enrolled_in_course,
)
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from .constants import (
    USERNAME,
    EMAIL,
    PASSWORD
)


class HelpersTestCase(ModuleStoreTestCase):
    """
    TestCase class for the helpers.py functions
    """

    def setUp(self):
        super(HelpersTestCase, self).setUp()
        self.user = UserFactory(username=USERNAME, email=EMAIL, password=PASSWORD)
        self.dummy_course = CourseFactory.create(display_name='test course 1', run='Testing_course_1')

    def test_is_user_enrolled_in_course(self):
        """
        Tests if the function correctly reports the enrollment status for a user-course pair.
        """
        self.assertFalse(is_user_enrolled_in_course(self.user.username, self.dummy_course.id))
        CourseEnrollmentFactory.create(user=self.user, course_id=self.dummy_course.id)
        self.assertTrue(is_user_enrolled_in_course(self.user.username, self.dummy_course.id))

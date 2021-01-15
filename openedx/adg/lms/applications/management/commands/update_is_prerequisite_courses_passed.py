"""
Management command to update is_prerequisite_courses_passed flag in ApplicationHub
"""
import logging
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from lms.djangoapps.grades.api import CourseGradeFactory
from openedx.adg.lms.applications.models import ApplicationHub, PrerequisiteCourseGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Updates is_prerequisite_courses_passed flag in ApplicationHub.
    """

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        prereq_course_groups = PrerequisiteCourseGroup.non_empty_prereq_course_groups()

        if not prereq_course_groups:
            sys.exit('Exiting!!! No open pre-req courses found but there must be some pre-reqs. Please add from admin')

        users_to_be_checked_for_update = self.get_minimal_users_to_be_checked_for_update(prereq_course_groups)

        if not users_to_be_checked_for_update:
            sys.exit('None of the users passed pre-req courses')

        self.check_users_for_application_update(users_to_be_checked_for_update, prereq_course_groups)

    def get_minimal_users_to_be_checked_for_update(self, prereq_course_groups):
        """
        Filter minimal set of users who should be checked for the update.
        Args:
            prereq_course_groups: List of course groups
        Returns:
            A list of user ids who should be checked for the update
        """
        # Exclude users who passed courses or do not have application
        users_to_be_checked_for_update = self.filter_user_by_application_hub_state()

        for prereq_course_group in prereq_course_groups:
            # Get user with valid course enrollment in prereq courses for current group
            user_ids = self.get_users_with_active_course_enrollments(
                users_to_be_checked_for_update, prereq_course_group
            )

            # Keep users who have active enrolments in each course group
            users_to_be_checked_for_update = list(set(users_to_be_checked_for_update).intersection(user_ids))

        return users_to_be_checked_for_update

    def filter_user_by_application_hub_state(self):
        """
        Get users who does not have associated application hub and if they have, then they have not passed all prereq
        courses
        Returns:
            A querySet for users who should be checked further
        """
        return User.objects.filter(
            Q(application_hub__isnull=True) | Q(application_hub__is_prerequisite_courses_passed=False),
        ).values_list('id', flat=True)

    def get_users_with_active_course_enrollments(self, users_to_be_checked_for_update, prereq_course_group):
        """
        Filter users from provided user ids. Filtered users that enrolled in one or more courses from course group
        and has not un-enrollment course
        Args:
            users_to_be_checked_for_update: List of user ids
            prereq_course_group: PrerequisiteCourseGroup model object
        Returns:
            A querySet for users who should be checked for the update
        """
        course_keys = prereq_course_group.course_keys()
        return User.objects.filter(
            id__in=users_to_be_checked_for_update,
            courseenrollment__course__in=course_keys,
            courseenrollment__is_active=True,
        ).values_list('id', flat=True).distinct()

    def check_users_for_application_update(self, users_to_be_checked_for_update, prereq_course_groups):
        """
        Check check passed prereq courses for all filtered users
        Args:
            users_to_be_checked_for_update: List of user ids
            prereq_course_groups: List of course groups
        Returns:
            None
        """
        users = User.objects.filter(id__in=users_to_be_checked_for_update)
        for user in users:
            self.check_passed_prereq_courses(user, prereq_course_groups)

    def check_passed_prereq_courses(self, user, prereq_course_groups):
        """
        Check passed prereq courses for a particular user and update application hub if all prereq courses are passed
        Args:
            user: User object
            prereq_course_groups: List of course groups
        Returns:
            None
        """
        for prereq_course_group in prereq_course_groups:
            if self.is_user_failed_in_course_group(user, prereq_course_group):
                logger.info('{username} has not yet passed all the pre-reqs'.format(username=user.username))
                break
        else:
            self.update_application_hub(user)

    def is_user_failed_in_course_group(self, user, prereq_course_group):
        """
        Checks if user is failed in the given group of courses. User is considered passed if he has passed any one of
        the courses from course group
        Args:
            user: User object
            prereq_course_group: PrerequisiteCourseGroup model object
        Returns:
            boolean, True if the course is failed otherwise False
        """
        course_keys = prereq_course_group.course_keys()

        for course_key in course_keys:
            course_grade = CourseGradeFactory().read(user, course_key=course_key)
            course_passed = course_grade and course_grade.passed

            if course_passed:
                is_failed = False
                break
        else:
            is_failed = True

        return is_failed

    def update_application_hub(self, user):
        """
        Update flag in application hub model for particular user, on successfully completing prereq courses
        Args:
            user: User object
        Returns:
            None
        """
        user_application_hub, _ = ApplicationHub.objects.get_or_create(user=user)
        user_application_hub.set_is_prerequisite_courses_passed()
        logger.info(
            '{username} has successfully completed the pre-reqs, flag is updated in application hub'.format(
                username=user.username
            )
        )

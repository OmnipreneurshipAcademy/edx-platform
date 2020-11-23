""" Management command to update is_prerequisite_courses_passed flag in ApplicationHub """
import logging
import sys

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from openedx.adg.lms.applications.models import ApplicationHub
from openedx.adg.lms.course_meta.models import CourseMeta
from openedx.adg.lms.utils.adg_utils import is_user_failed_in_course

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Updates is_prerequisite_courses_passed flag in ApplicationHub.
    """
    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        pre_req_courses = CourseMeta.open_pre_req_courses.all()

        if not pre_req_courses:
            sys.exit('Exiting!!! No open pre-req courses found. But there must be some pre-reqs. Please add in admin.')

        users_to_be_checked_for_update = self.get_minimal_users_to_be_checked_for_update(pre_req_courses)
        for user in users_to_be_checked_for_update:
            for pre_req_course in pre_req_courses:
                if is_user_failed_in_course(user, pre_req_course):
                    logger.info('{username} has not yet passed all the pre-reqs'.format(username=user.username))
                    break
            else:
                user_application_hub, _ = ApplicationHub.objects.get_or_create(user=user)
                user_application_hub.set_is_prerequisite_courses_passed()
                logger.info(
                    '{username} has successfully completed the pre-reqs, flag is updated in application hub'.format(
                        username=user.username
                    )
                )

    def get_minimal_users_to_be_checked_for_update(self, pre_req_courses):
        """
        Filter minimal set of users who should be checked for the update.
        Args:
            pre_req_courses: List
        Returns:
            A querySet for users who should be checked for the update
        """
        return User.objects.filter(
            Q(application_hub__isnull=True) | Q(application_hub__is_prerequisite_courses_passed=False),
            courseenrollment__course__in=pre_req_courses,
            courseenrollment__is_active=True,
        ).annotate(
            num_of_enrolled_pre_reqs=Count('username')
        ).filter(
            num_of_enrolled_pre_reqs=len(pre_req_courses)
        )

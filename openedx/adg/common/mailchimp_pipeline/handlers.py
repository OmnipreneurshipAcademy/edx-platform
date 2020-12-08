"""
Signals for Mailchimp pipeline
"""
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from openedx.adg.lms.applications.models import UserApplication
from openedx.adg.lms.registration_extension.models import ExtendedUserProfile
from openedx.adg.lms.utils.decorators import suspendingreceiver
from student.models import EnrollStatusChange, UserProfile
from student.signals import ENROLL_STATUS_CHANGE

from .helpers import (
    get_extendeduserprofile_merge_fields,
    get_user_merge_fields,
    get_userapplication_merge_fields,
    get_userprofile_merge_fields,
    is_mailchimp_sync_required
)
from .tasks import task_send_user_enrollments_to_mailchimp, task_send_user_info_to_mailchimp


@suspendingreceiver(post_save, sender=ExtendedUserProfile)
@suspendingreceiver(post_save, sender=UserProfile)
@suspendingreceiver(post_save, sender=UserApplication)
@suspendingreceiver(post_save, sender=User)
def send_user_info_to_mailchimp(sender, created, instance, **kwargs):
    """
    Listens for User and User related model changes and syncs data with mailchimp.

    We need to sync data to mailchimp and data required for mailchimp exists in multiple models.
    We will sync in following scenarios:
    1. Any of the sender is created.
    2. UserProfile is created or updated. (We don't have `update_fields` in kwargs)
    3. UserApplication and ExtendedUserProfile is created or `update_fields` has one of the mailchimp req fields.

    Args:
        sender (obj): The sender of the signal.
        instance (obj): Object which is created or updated.
        created (boolean): True if user object is created, False if user updated.
        **kwargs (dict): Additional parameters.

    Returns:
        None
    """
    if not is_mailchimp_sync_required(created, sender, **kwargs):
        return

    MERGE_FIELDS_CALLABLES = {
        'get_user_merge_fields': get_user_merge_fields,
        'get_userprofile_merge_fields': get_userprofile_merge_fields,
        'get_userapplication_merge_fields': get_userapplication_merge_fields,
        'get_extendeduserprofile_merge_fields': get_extendeduserprofile_merge_fields
    }

    user_email = instance.email if sender == User else instance.user.email
    user_json = {
        'email_address': user_email,
        'status_if_new': 'subscribed',
        'merge_fields': {}
    }

    sender_callable_name = 'get_{}_merge_fields'.format(sender.__name__.lower())
    user_json['merge_fields'].update(MERGE_FIELDS_CALLABLES[sender_callable_name](instance))

    task_send_user_info_to_mailchimp.delay(user_email, user_json)


@suspendingreceiver(ENROLL_STATUS_CHANGE)
def send_user_enrollments_to_mailchimp(sender, event=None, **kwargs):  # pylint: disable=unused-argument
    """
    Listen for course enrollment events (enrollment and un-enrollment) and call task for syncing enrollment
    with Mailchimp.

    Args:
        sender (obj): The sender of the signal
        event (string): Signal name
        **kwargs (dict): Additional parameters

    Returns:
        None
    """
    if event not in [EnrollStatusChange.enroll, EnrollStatusChange.unenroll]:
        return

    task_send_user_enrollments_to_mailchimp.delay(kwargs.get('user').id, kwargs['course_id'])

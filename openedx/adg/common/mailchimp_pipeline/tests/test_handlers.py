"""
All tests for mailchimp pipeline handlers
"""
import pytest
from django.test.utils import override_settings

from openedx.adg.common.mailchimp_pipeline.helpers import (
    get_extendeduserprofile_merge_fields,
    get_user_merge_fields,
    get_userapplication_merge_fields,
    get_userprofile_merge_fields
)
from openedx.adg.lms.applications.test.factories import UserApplicationFactory
from openedx.adg.lms.registration_extension.tests.factories import ExtendedUserProfileFactory
from openedx.core.djangolib.testing.utils import skip_unless_lms
from student.models import EnrollStatusChange
from student.tests.factories import UserFactory


# pylint: disable=redefined-outer-name
@pytest.fixture
@override_settings(SUSPEND_RECEIVERS=False)
def mailchimp_handlers(request):
    """
    A fixture for mailchimp handlers. Importing handler module inside test to override settings.
    """
    from openedx.adg.common.mailchimp_pipeline import handlers as mailchimp_handlers
    return mailchimp_handlers


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
def test_send_user_info_to_mailchimp_user_created(mocker, mailchimp_handlers):
    """
    Assert that `send_user_info_to_mailchimp` called with appropriate params and celery task for sync
    is called specific number of times as per the object creation and is called with the given params.
    """
    mock_task = mocker.patch.object(mailchimp_handlers, 'task_send_user_info_to_mailchimp')
    instance = UserFactory()
    profile = instance.profile
    user_email = instance.email

    base_user_info = {
        'email_address': user_email,
        'status_if_new': 'subscribed',
    }
    user_json = {
        **base_user_info,
        'merge_fields': get_user_merge_fields(instance),
    }
    profile_json = {
        **base_user_info,
        'merge_fields': get_userprofile_merge_fields(profile),
    }

    profile.name = 'dummy user'
    profile.save()  # pylint: disable=no-member
    profile_updated_json = {
        **base_user_info,
        'merge_fields': get_userprofile_merge_fields(profile),
    }

    assert mock_task.delay.call_count == 3
    mock_task.delay.assert_any_call(user_email, user_json)
    mock_task.delay.assert_any_call(user_email, profile_json)
    mock_task.delay.assert_any_call(user_email, profile_updated_json)


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
def test_send_user_info_to_mailchimp_user_updated(mocker, mailchimp_handlers):
    """
    Assert that `send_user_info_to_mailchimp` called with appropriate params and celery task for sync is called
    specific number of times and is not called for User update.
    """
    mock_task = mocker.patch.object(mailchimp_handlers, 'task_send_user_info_to_mailchimp')
    instance = UserFactory()
    instance.username = 'dummyuser'
    instance.save()

    assert mock_task.delay.call_count == 2


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
@skip_unless_lms
def test_send_user_info_to_mailchimp_application_fields(mocker, mailchimp_handlers):
    """
    Assert that `send_user_info_to_mailchimp` called with appropriate params and sync with mailchimp task is called
    specific number of times when application is created, `update_fields` contains UserApplication field which is
    required at mailchimp and is not called when `update_fields` is empty.
    """
    mock_task = mocker.patch.object(mailchimp_handlers, 'task_send_user_info_to_mailchimp')
    instance = UserApplicationFactory()
    user_email = instance.user.email

    base_user_json = {
        'email_address': user_email,
        'status_if_new': 'subscribed',
    }
    user_json = {
        **base_user_json,
        'merge_fields': get_userapplication_merge_fields(instance)
    }

    instance.organization = 'dummy org'
    instance.save(update_fields=('organization',))

    user_app_updated_json = {
        **base_user_json,
        'merge_fields': get_userapplication_merge_fields(instance)
    }

    instance.organization = 'dummy org2'
    instance.save()

    assert mock_task.delay.call_count == 4
    mock_task.delay.assert_any_call(user_email, user_json)
    mock_task.delay.assert_any_call(user_email, user_app_updated_json)


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
@skip_unless_lms
def test_send_user_info_to_mailchimp_user_company_updated(mocker, mailchimp_handlers):
    """
    Assert that `send_user_info_to_mailchimp` called with appropriate params and sync with mailchimp task is called
    specific number of times when object of ExtendedUserProfile is created.
    """
    mock_task = mocker.patch.object(mailchimp_handlers, 'task_send_user_info_to_mailchimp')
    instance = ExtendedUserProfileFactory()
    user_email = instance.user.email

    base_user_json = {
        'email_address': user_email,
        'status_if_new': 'subscribed',
    }
    user_json = {
        **base_user_json,
        'merge_fields': get_extendeduserprofile_merge_fields(instance)
    }

    assert mock_task.delay.call_count == 3
    mock_task.delay.assert_any_call(user_email, user_json)


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
def test_send_user_enrollments_to_mailchimp_with_valid_enrollment_event(mocker, mailchimp_handlers):
    """
    Assert that `send_user_enrollments_to_mailchimp` called with appropriate params
    """
    event = EnrollStatusChange.enroll
    dummy_kwargs = {'user': 'dummy', 'course': 'test_course'}
    mock_call = mocker.patch.object(mailchimp_handlers, 'task_send_user_enrollments_to_mailchimp')

    mailchimp_handlers.send_user_enrollments_to_mailchimp(sender=None, event=event, **dummy_kwargs)

    mock_call.delay.assert_called_once_with(**dummy_kwargs)


@pytest.mark.django_db
@override_settings(SUSPEND_RECEIVERS=False)
def test_send_user_enrollments_to_mailchimp_different_enrollment_event(mocker, mailchimp_handlers):
    """
    Assert that `send_user_enrollments_to_mailchimp` not called when signal event is other than enrollment
    or un-enrollment
    """
    mock_call = mocker.patch.object(mailchimp_handlers, 'task_send_user_enrollments_to_mailchimp')

    mailchimp_handlers.send_user_enrollments_to_mailchimp(sender=None, event=EnrollStatusChange.upgrade_complete)

    assert not mock_call.delay.called

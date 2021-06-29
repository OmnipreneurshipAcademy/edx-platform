"""
All tests for webinars handlers functions
"""
import pytest

from openedx.adg.lms.webinars.tests.factories import WebinarRegistrationFactory


@pytest.mark.django_db
def test_cancel_reminder_emails(mocker):
    """
    Test that upon deleting webinar registrations, reminder emails of registered users
    and webinar team members are cancelled
    """
    mock_cancel_all_reminders = mocker.patch('openedx.adg.lms.webinars.handlers.cancel_all_reminders')

    registration_1 = WebinarRegistrationFactory(is_registered=False)
    registration_2 = WebinarRegistrationFactory(is_registered=True)
    registration_3 = WebinarRegistrationFactory(is_team_member_registration=True)

    registration_1.delete()
    mock_cancel_all_reminders.assert_not_called()

    registration_2.delete()
    mock_cancel_all_reminders.assert_called_once()

    registration_3.delete()
    assert mock_cancel_all_reminders.call_count == 2

"""
All tests for webinar tasks
"""
from datetime import datetime, timedelta

import pytest

from openedx.adg.lms.webinars.constants import WEBINARS_TIME_FORMAT
from openedx.adg.lms.webinars.tasks import task_reschedule_webinar_reminders

from .factories import WebinarRegistrationFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    'new_start_time, expected_call_count', [
        (datetime.now() + timedelta(days=1), 1),
        (datetime.now() + timedelta(days=8), 2),
    ]
)
def test_task_send_mandrill_email_successfully(new_start_time, expected_call_count, mocker, webinar):
    """
    Tests if reschedule_webinar_reminders is called properly when the start_time is updated.
    """
    mock_reschedule = mocker.patch('openedx.adg.lms.webinars.tasks.reschedule_webinar_reminders')

    WebinarRegistrationFactory(webinar=webinar)

    task_reschedule_webinar_reminders(webinar.id, new_start_time.strftime(WEBINARS_TIME_FORMAT))

    assert expected_call_count == mock_reschedule.call_count

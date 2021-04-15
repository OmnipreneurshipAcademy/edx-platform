"""
All tests for webinars forms
"""
import pytest
from django.forms.models import model_to_dict

from openedx.adg.lms.webinars.forms import WebinarForm


@pytest.mark.parametrize(
    'emails , expected_result', [
            ('test1@exmaple.com,test2@example.com', True),
            ('test1@exmaple.com,test2.example.com', False)
        ]
    )
@pytest.mark.django_db
def test_webinar_form_with_emails(webinar, emails, expected_result):
    """
    Test that only valid emails are allowed in invites_by_email_address field
    """
    data = model_to_dict(webinar)
    data['invites_by_email_address'] = emails
    form = WebinarForm(data=data, files={'banner': webinar.banner})
    assert form.is_valid() == expected_result
    webinar.banner.close()

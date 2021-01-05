"""
All tests for applications helpers functions
"""
from unittest.mock import Mock, patch

import pytest

from openedx.adg.lms.applications.constants import LOGO_IMAGE_MAX_SIZE, RESUME_FILE_MAX_SIZE
from openedx.adg.lms.applications.helpers import (
    send_application_submission_confirmation_email,
    validate_file_size,
    validate_logo_size
)

from .constants import EMAIL


def test_validate_logo_size_with_valid_size():
    """
    Verify that file size up to LOGO_IMAGE_MAX_SIZE is allowed
    """
    mocked_file = Mock()
    mocked_file.size = LOGO_IMAGE_MAX_SIZE
    validate_logo_size(mocked_file)


def test_validate_logo_size_with_invalid_size():
    """
    Verify that size greater than LOGO_IMAGE_MAX_SIZE is not allowed
    """
    mocked_file = Mock()
    mocked_file.size = LOGO_IMAGE_MAX_SIZE + 1
    with pytest.raises(Exception):
        validate_logo_size(mocked_file)


@patch('openedx.adg.lms.applications.helpers.send_mandrill_email')
def test_send_application_submission_confirmation_email(mock_mandrill_email):
    """
    Check if the email is being sent correctly
    """
    send_application_submission_confirmation_email(EMAIL)
    assert mock_mandrill_email.called


@pytest.mark.parametrize('size , expected', [
    (RESUME_FILE_MAX_SIZE, None),
    (RESUME_FILE_MAX_SIZE+1, 'File size must not exceed 4.0 MB')
])
def test_validate_file_size_with_valid_size(size, expected):
    """
    Verify that file size up to max_size i.e. RESUME_FILE_MAX_SIZE is allowed
    """
    mocked_file = Mock()
    mocked_file.size = size
    error = validate_file_size(mocked_file, RESUME_FILE_MAX_SIZE)
    assert error == expected

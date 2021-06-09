"""
All tests for applications helpers functions
"""
from datetime import date
from unittest.mock import Mock, patch

import mock
import pytest
from django.core.exceptions import ValidationError

from common.djangoapps.student.tests.factories import UserFactory
from openedx.adg.lms.applications.constants import (
    FILE_MAX_SIZE,
    INTEREST,
    LOGO_IMAGE_MAX_SIZE,
    MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT,
    MAXIMUM_YEAR_OPTION,
    MINIMUM_YEAR_OPTION,
    MONTH_NAME_DAY_YEAR_FORMAT,
    SCORES
)
from openedx.adg.lms.applications.helpers import (
    _get_application_review_info,
    check_validations_for_current_record,
    check_validations_for_past_record,
    get_duration,
    get_extra_context_for_application_review_page,
    has_admin_permissions,
    max_year_value_validator,
    min_year_value_validator,
    send_application_submission_confirmation_email,
    validate_file_size,
    validate_logo_size,
    validate_word_limit
)
from openedx.adg.lms.applications.models import UserApplication

from .constants import EMAIL, TEST_TEXT_INPUT

DATE_COMPLETED_MONTH = 5
DATE_COMPLETED_YEAR = 2020
DATE_STARTED_MONTH = 2
DATE_STARTED_YEAR = 2018
ERROR_MESSAGE = '{key}, some error message'


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


@patch('openedx.adg.lms.applications.helpers.task_send_mandrill_email')
def test_send_application_submission_confirmation_email(mocked_task_send_mandrill_email):
    """
    Check if the email is being sent correctly
    """
    send_application_submission_confirmation_email(EMAIL)
    assert mocked_task_send_mandrill_email.delay.called


def test_min_year_value_validator_invalid():
    """
    Check if invalid value for min year value validator raises error
    """
    with pytest.raises(ValidationError):
        min_year_value_validator(MINIMUM_YEAR_OPTION - 1)


def test_min_year_value_validator_valid():
    """
    Check if invalid value for min year value validator raises error
    """
    assert min_year_value_validator(MINIMUM_YEAR_OPTION) is None


def test_max_year_value_validator_invalid():
    """
    Check if invalid value for max year value validator raises error
    """
    with pytest.raises(ValidationError):
        max_year_value_validator(MAXIMUM_YEAR_OPTION + 1)


def test_max_year_value_validator_valid():
    """
    Check if invalid value for max year value validator raises error
    """
    assert max_year_value_validator(MAXIMUM_YEAR_OPTION) is None


@pytest.mark.parametrize('date_attrs_with_expected_results', [
    {
        'attrs': {
            'date_started_month': 1,
            'date_started_year': date.today().year - 1,
        },
        'expected_result': {}
    },
    {
        'attrs': {
            'date_started_month': 1,
            'date_started_year': date.today().year - 1,
            'date_completed_month': DATE_COMPLETED_MONTH
        },
        'expected_result': {
            'date_completed_month': ERROR_MESSAGE.format(key='Date completed month')
        }
    },
    {
        'attrs': {
            'date_started_month': 1,
            'date_started_year': date.today().year - 1,
            'date_completed_year': DATE_COMPLETED_YEAR
        },
        'expected_result': {
            'date_completed_year': ERROR_MESSAGE.format(key='Date completed year')
        }
    },
    {
        'attrs': {
            'date_started_month': 1,
            'date_started_year': date.today().year + 1,
            'date_completed_month': DATE_COMPLETED_MONTH,
            'date_completed_year': DATE_COMPLETED_YEAR,
        },
        'expected_result': {
            'date_completed_month': ERROR_MESSAGE.format(key='Date completed month'),
            'date_completed_year': ERROR_MESSAGE.format(key='Date completed year'),
            'date_started_year': 'Date should not be in future',
        }
    },
])
def test_check_validations_for_current_record(date_attrs_with_expected_results):
    """
    Check for expected validation errors against provided data
    """
    actual_result = check_validations_for_current_record(date_attrs_with_expected_results['attrs'], ERROR_MESSAGE)
    assert actual_result == date_attrs_with_expected_results['expected_result']


@pytest.mark.parametrize('date_attrs_with_expected_results', [
    {
        'attrs': {'date_started_month': DATE_COMPLETED_MONTH, 'date_started_year': DATE_COMPLETED_YEAR},
        'expected_result': {
            'date_completed_month': ERROR_MESSAGE.format(key='Date completed month'),
            'date_completed_year': ERROR_MESSAGE.format(key='Date completed year')
        }
    },
    {
        'attrs': {
            'date_completed_month': DATE_COMPLETED_MONTH,
            'date_started_month': DATE_STARTED_MONTH,
            'date_started_year': DATE_STARTED_YEAR
        },
        'expected_result': {'date_completed_year': ERROR_MESSAGE.format(key='Date completed year')}
    },
    {
        'attrs': {
            'date_completed_year': DATE_COMPLETED_YEAR,
            'date_started_month': DATE_STARTED_MONTH,
            'date_started_year': DATE_STARTED_YEAR
        },
        'expected_result': {'date_completed_month': ERROR_MESSAGE.format(key='Date completed month')}
    },
    {
        'attrs': {
            'date_completed_month': DATE_COMPLETED_MONTH,
            'date_completed_year': DATE_COMPLETED_YEAR,
            'date_started_month': DATE_STARTED_MONTH,
            'date_started_year': DATE_STARTED_YEAR
        },
        'expected_result': {}
    },
    {
        'attrs': {
            'date_completed_month': DATE_COMPLETED_MONTH,
            'date_completed_year': DATE_COMPLETED_YEAR,
            'date_started_month': DATE_STARTED_MONTH,
            'date_started_year': DATE_COMPLETED_YEAR + 1
        },
        'expected_result': {'date_completed_year': 'Completed date must be greater than started date.'}
    }
])
def test_check_validations_for_past_record(date_attrs_with_expected_results):
    """
    Check for expected validation errors against provided data
    """
    actual_result = check_validations_for_past_record(date_attrs_with_expected_results['attrs'], ERROR_MESSAGE)
    assert actual_result == date_attrs_with_expected_results['expected_result']


@pytest.mark.parametrize('size , expected', [
    (FILE_MAX_SIZE, None),
    (FILE_MAX_SIZE + 1, 'File size must not exceed 4.0 MB')
])
def test_validate_file_size_with_valid_size(size, expected):
    """
    Verify that file size up to max_size i.e. FILE_MAX_SIZE is allowed
    """
    mocked_file = Mock()
    mocked_file.size = size
    error = validate_file_size(mocked_file, FILE_MAX_SIZE)
    assert error == expected


@pytest.mark.parametrize(
    'is_current, expected_duration', [
        (True, 'January 2020 to Present'),
        (False, 'January 2020 to December 2020')
    ]
)
@pytest.mark.django_db
def test_get_duration(is_current, expected_duration, work_experience):
    """
    Test that the `get_duration` function returns the time duration in the correct format when provided with a
    `UserStartAndEndDates` entry.
    """
    work_experience.date_started_month = 1
    work_experience.date_started_year = 2020

    if not is_current:
        work_experience.date_completed_month = 12
        work_experience.date_completed_year = 2020

    actual_duration = get_duration(work_experience, is_current)

    assert expected_duration == actual_duration


@pytest.mark.parametrize(
    'application_status', [UserApplication.OPEN, UserApplication.WAITLIST]
)
@pytest.mark.django_db
def test_get_application_review_info(user_application, application_status):
    """
    Test that the `_get_application_review_info` function extracts and returns the correct reviewer and review date from
    the input application, depending upon the application status.
    """
    user_application.status = application_status

    if application_status == UserApplication.OPEN:
        expected_reviewed_by = None
        expected_review_date = None
    else:
        reviewer = UserFactory()
        user_application.reviewed_by = reviewer

        current_date = date.today()
        user_application.modified = current_date

        expected_reviewed_by = reviewer.profile.name
        expected_review_date = current_date.strftime(MONTH_NAME_DAY_YEAR_FORMAT)

    expected_review_info = expected_reviewed_by, expected_review_date
    actual_review_info = _get_application_review_info(user_application)

    assert expected_review_info == actual_review_info


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.helpers._get_application_review_info')
def test_get_extra_context_for_application_review_page(mock_get_application_review_info, user_application):
    """
    Test that the `get_extra_context_for_application_review_page` function returns the correct context when provided
    with an application.
    """
    mock_get_application_review_info.return_value = 'reviewed_by', 'review_date'

    expected_context = {
        'title': user_application.user.profile.name,
        'adg_view': True,
        'application': user_application,
        'reviewer': 'reviewed_by',
        'review_date': 'review_date',
        'SCORES': SCORES,
        'INTEREST': INTEREST,
    }
    actual_context = get_extra_context_for_application_review_page(user_application)

    assert expected_context == actual_context


@pytest.mark.django_db
@pytest.mark.parametrize(
    'is_staff, is_superuser, is_business_line_admin, expected_result',
    [
        (False, False, False, False),
        (False, False, True, False),
        (False, True, False, False),
        (False, True, True, False),
        (True, False, False, False),
        (True, False, True, True),
        (True, True, False, True),
        (True, True, True, True),
    ]
)
def test_has_admin_permissions(mocker, is_business_line_admin, is_superuser, is_staff, expected_result):
    """
    Test if the user is a superuser or an ADG admin or the admin of any Business line while having the staff
    status
    """
    mocked_class = mocker.patch('openedx.adg.lms.applications.models.BusinessLine')
    mocked_class.is_user_business_line_admin.return_value = is_business_line_admin

    test_user = UserFactory(is_superuser=is_superuser, is_staff=is_staff)

    assert has_admin_permissions(test_user) == expected_result


@pytest.mark.parametrize('text_input, is_valid', [
    (TEST_TEXT_INPUT, True),
    (TEST_TEXT_INPUT * MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT, True),
    (TEST_TEXT_INPUT * (MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT + 1), False)
])
@pytest.mark.django_db
def test_validate_word_limit(text_input, is_valid):
    """
    Check if the `validate_word_limit` function raises a ValidationError if the total
    number of words exceed the provided limit
    """
    if is_valid:
        assert not validate_word_limit(text_input)
    else:
        with pytest.raises(ValidationError):
            validate_word_limit(text_input)

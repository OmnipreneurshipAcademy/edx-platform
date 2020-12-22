"""
Helper methods for applications
"""
import os

from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError

from django.core.validators import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext as _

from openedx.adg.common.lib.mandrill_client.client import MandrillClient
from openedx.adg.lms.student.helpers import send_mandrill_email
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

from .constants import LOGO_IMAGE_MAX_SIZE, MAXIMUM_YEAR_OPTION, MINIMUM_YEAR_OPTION
from django.utils.html import format_html


def validate_logo_size(file_):
    """
    Validate maximum allowed file upload size, raise validation error if file size exceeds.

    Arguments:
         file_(object): file that needs to be validated for size

    Returns:
        None
    """
    size = getattr(file_, 'size', None)
    if size and LOGO_IMAGE_MAX_SIZE < size:
        raise ValidationError(_('File size must not exceed {size} KB').format(size=LOGO_IMAGE_MAX_SIZE / 1024))


# pylint: disable=translation-of-non-string
def check_validations_for_past_record(attrs, error_message):
    """
    Check for validation errors for past record

    Arguments:
        attrs (dict): dictionary contains all attributes
        error_message (str): Error message for validations

    Returns:
        dict: contains error messages
    """
    errors = {}

    if not attrs.get('date_completed_month', False):
        errors['date_completed_month'] = _(error_message).format(key='Date completed month')

    if not attrs.get('date_completed_year', False):
        errors['date_completed_year'] = _(error_message).format(key='Date completed year')

    started_date = datetime(year=attrs['date_started_year'], month=attrs['date_started_month'], day=1)

    if attrs.get('date_completed_month') and attrs.get('date_completed_year'):
        completed_date = datetime(year=attrs['date_completed_year'], month=attrs['date_completed_month'], day=1)

        if completed_date <= started_date:
            errors['date_completed_year'] = _('Completion date must comes after started date')

    return errors


def check_validations_for_current_record(attrs, error_message):
    """
    Check for validation errors for current record

    Arguments:
        attrs (dict): dictionary contains all attributes
        error_message (str): Error message for validations

    Returns:
        dict: contains error messages
    """
    errors = {}

    if attrs.get('date_completed_month'):
        errors['date_completed_month'] = _(error_message).format(key='Date completed month')

    if attrs.get('date_completed_year'):
        errors['date_completed_year'] = _(error_message).format(key='Date completed year')

    return errors


def send_application_submission_confirmation_email(recipient_email):
    """
    Send an email to the recipient_email according to the mandrill template

    Args:
        recipient_email(str): target email address to send the email to

    Returns:
        None
    """
    root_url = configuration_helpers.get_value('LMS_ROOT_URL', settings.LMS_ROOT_URL)
    course_catalog_url = '{root_url}{course_catalog_url}'.format(
        root_url=root_url,
        course_catalog_url=reverse('courses')
    )

    context = {
        'course_catalog_url': course_catalog_url
    }
    send_mandrill_email(MandrillClient.APPLICATION_SUBMISSION_CONFIRMATION, recipient_email, context)


def min_year_value_validator(value):
    """
    Minimum value validator for year fields in UserStartAndEndDates model.

    Args:
        value (Int): Value to save as year
    """
    return MinValueValidator(MINIMUM_YEAR_OPTION)(value)


def max_year_value_validator(value):
    """
    Maximum value validator for year fields in UserStartAndEndDates model.

    Args:
        value (Int): Value to save as year
    """
    return MaxValueValidator(MAXIMUM_YEAR_OPTION)(value)


def validate_file_size(data_file, max_size):
    """
    Validate maximum allowed file upload size, return error if file size exceeds, else return None.

    Arguments:
         data_file(object): file that needs to be validated for size
         max_size(int): Maximum size allowed for file

    Returns:
        str: Error message if validation fails
    """
    size = getattr(data_file, 'size', None)
    if size and max_size < size:
        return _('File size must not exceed {size} MB').format(size=max_size / 1024 / 1024)
    return None


def can_display_file(file):
    filename = str(file)
    if not filename.endswith('doc'):
        return True


def display_file(file):
    """
    Return html to display image or embedded view for pdf

    Arguments:
        file (File): file that needs to be rendered
    """
    _name, ext = os.path.splitext(str(file))
    if ext in ['.jpg', '.png']:
        html = '<img src="{path_to_image}"/>'.format(path_to_image=file.url)
    else:  # for pdf
        html = '<iframe src="{path_to_file}" style="width:600px; height:500px;"></iframe>'.format(path_to_file=file.url)

    return format_html(html)


def display_start_and_end_date(entry, is_current):
    """
    Extract, format and return start and end date of Education/WorkExperience

    Arguments:
        entry (UserStartAndEndDates): Education or WorkExperience object
        is_current (bool): True if Education is in progress or WorkExperience is current position

    Returns:
        str: start and end date
    """
    start_date = '{month} {year}'.format(month=entry.get_date_started_month_display(), year=entry.date_started_year)
    completed_date = 'Present' if is_current else '{month} {year}'.format(
        month=entry.get_date_completed_month_display(), year=entry.date_completed_year
    )
    return '{started} to {completed}'.format(started=start_date, completed=completed_date)

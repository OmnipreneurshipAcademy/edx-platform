"""
Helper methods for applications
"""
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
from django.urls import reverse
from django.utils.translation import gettext as _

from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.util.milestones_helpers import get_prerequisite_courses_display
from lms.djangoapps.courseware.models import StudentModule
from lms.djangoapps.grades.api import CourseGradeFactory
from openedx.adg.common.lib.mandrill_client.client import MandrillClient
from openedx.adg.common.lib.mandrill_client.tasks import task_send_mandrill_email
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.lib.grade_utils import round_away_from_zero
from xmodule.modulestore.django import modulestore

from .constants import (
    APPLICATION_SUBMISSION_CONGRATS,
    APPLICATION_SUBMISSION_INSTRUCTION,
    COMPLETED,
    IN_PROGRESS,
    INTEREST,
    LOCKED,
    LOCKED_COURSE_MESSAGE,
    LOGO_IMAGE_MAX_SIZE,
    MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT,
    MAXIMUM_YEAR_OPTION,
    MINIMUM_YEAR_OPTION,
    MONTH_NAME_DAY_YEAR_FORMAT,
    NOT_STARTED,
    PREREQUISITE_COURSES_COMPLETION_CONGRATS,
    PREREQUISITE_COURSES_COMPLETION_INSTRUCTION,
    PREREQUISITE_COURSES_COMPLETION_MSG,
    RETAKE,
    RETAKE_COURSE_MESSAGE,
    SCORES,
    WRITTEN_APPLICATION_COMPLETION_CONGRATS,
    WRITTEN_APPLICATION_COMPLETION_INSTRUCTION,
    WRITTEN_APPLICATION_COMPLETION_MSG
)
from .rules import is_adg_admin


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

    started_date = datetime(year=attrs['date_started_year'], month=attrs['date_started_month'], day=1)
    errors = update_errors_if_future_date(started_date, errors, 'date_started_year')

    if not attrs.get('date_completed_month', False):
        errors['date_completed_month'] = _(error_message).format(key='Date completed month')

    if not attrs.get('date_completed_year', False):
        errors['date_completed_year'] = _(error_message).format(key='Date completed year')

    if attrs.get('date_completed_month') and attrs.get('date_completed_year'):
        completed_date = datetime(year=attrs['date_completed_year'], month=attrs['date_completed_month'], day=1)

        if completed_date <= started_date:
            errors['date_completed_year'] = _('Completed date must be greater than started date.')

        errors = update_errors_if_future_date(completed_date, errors, 'date_completed_year')

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

    started_date = datetime(year=attrs['date_started_year'], month=attrs['date_started_month'], day=1)
    errors = update_errors_if_future_date(started_date, errors, 'date_started_year')

    if attrs.get('date_completed_month'):
        errors['date_completed_month'] = _(error_message).format(key='Date completed month')

    if attrs.get('date_completed_year'):
        errors['date_completed_year'] = _(error_message).format(key='Date completed year')

    return errors


def update_errors_if_future_date(date, errors, key):
    """
    Update errors dict if date is in future

    Arguments:
        date (datetime): date that needs to be checked
        errors (dict): error messages dict that needs to be updated
        key (str): field key for adding error

    Returns:
        dict: contains updated error messages
    """
    if datetime.now() <= date:
        errors[key] = _('Date should not be in future')

    return errors


def validate_word_limit(text_area_input):
    """
    Validate that the text input does not exceed the word limit

    Arguments:
        text_area_input (str): String input from the textarea

    Returns:
        None
    """
    if text_area_input is None:
        return

    all_words = text_area_input.strip().split(' ')
    non_empty_words = [word for word in all_words if word]
    total_num_of_words = len(non_empty_words)
    if total_num_of_words > MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT:
        raise ValidationError(
            _('This field cannot exceed {max_words} words').format(max_words=MAX_NUMBER_OF_WORDS_ALLOWED_IN_TEXT_INPUT)
        )


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
    task_send_mandrill_email.delay(MandrillClient.APPLICATION_SUBMISSION_CONFIRMATION, [recipient_email], context)


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


def get_duration(entry, is_current):
    """
    Extract, format and return start and end date of Education/WorkExperience

    Arguments:
        entry (UserStartAndEndDates): Education or WorkExperience object
        is_current (bool): True if Education is in progress or WorkExperience is current position

    Returns:
        str: start and end date
    """
    start_date = '{month} {year}'.format(month=entry.get_date_started_month_display(), year=entry.date_started_year)
    completed_date = _('Present') if is_current else '{month} {year}'.format(
        month=entry.get_date_completed_month_display(), year=entry.date_completed_year
    )
    return '{started} {to} {completed}'.format(started=start_date, to=_('to'), completed=completed_date)


def _get_application_review_info(application):
    """
    Get application review information if the application has been reviewed, i.e. application status is not 'open'

    Arguments:
        application (UserApplication): User application

    Returns:
        reviewed_by (str): Name of reviewer
        review_date (str): Date of review submission
    """
    reviewed_by = None
    review_date = None
    if application.status != application.OPEN:
        reviewed_by = application.reviewed_by.profile.name
        review_date = application.modified.strftime(MONTH_NAME_DAY_YEAR_FORMAT)

    return reviewed_by, review_date


def get_extra_context_for_application_review_page(application):
    """
    Prepare and return extra context for application review page

    Arguments:
        application (UserApplication): Application under review

    Returns:
        dict: extra context
    """
    name_of_applicant = application.user.profile.name

    reviewed_by, review_date = _get_application_review_info(application)

    extra_context = {
        'title': name_of_applicant,
        'adg_view': True,
        'application': application,
        'reviewer': reviewed_by,
        'review_date': review_date,
        'SCORES': SCORES,
        'INTEREST': INTEREST,
    }

    return extra_context


def has_admin_permissions(user):
    """
    Checks if the user is a superuser or an ADG admin or the admin of any business line while having the staff status

    Arguments:
        user (User): User object to check for permissions

    Returns:
        boolean: True if the user has admin permissions of any kind else False
    """
    from openedx.adg.lms.applications.models import BusinessLine

    is_user_admin = user.is_superuser or is_adg_admin(user) or BusinessLine.is_user_business_line_admin(user)
    return user.is_staff and is_user_admin


def get_courses_from_course_groups(course_groups, user):
    """
    Get courses from the given course groups for the user.

    Args:
        course_groups (list): List of course groups
        user (User): User for which courses will be returned

    Returns:
        list: List of courses for the user
    """
    courses_list = []
    for course_group in course_groups:
        open_multilingual_courses = course_group.multilingual_courses.open_multilingual_courses()
        multilingual_course = open_multilingual_courses.multilingual_course(user)

        if multilingual_course:
            courses_list.append(multilingual_course.course)

    return courses_list


def get_course_card_information(user, courses):
    """
    Decides status, grade and message for each course in the list and appends a dictionary containing status, grade,
    message and course itself in a list

    Arguments:
        user (User): User object
        courses (list): List containing Course objects

    Returns:
        course_cards_information (list): A list containing dictionaries with status, grade, message and course
        is_any_course_started (bool): Flag indicating if any course has been started yet
        is_locked (bool): Flag indicating if any course is locked
    """
    course_cards_information = []
    is_any_course_started = False
    is_locked = False

    for course in courses:
        message = grade = status = ''
        pre_requisite_courses = get_prerequisite_courses_display(course)

        if pre_requisite_courses:
            is_locked, status, message = get_information_for_course_with_prerequisites(
                user, pre_requisite_courses, is_locked, status
            )

        if status != LOCKED:
            is_any_course_started, status, grade, message = get_information_for_unlocked_course(
                user, course, is_any_course_started, grade
            )

        course_cards_information.append({
            'course': course,
            'status': status,
            'grade': grade,
            'message': message
        })

    return course_cards_information, is_any_course_started, is_locked


def get_information_for_course_with_prerequisites(user, pre_requisite_courses, is_locked, status):
    """
    Checks if all prerequisite courses have been passed, if not then changes the status to Locked, sets the is_locked
    flag to True and returns a message advising the user to pass the prerequisite courses.

    Arguments:
        user (User): User object
        pre_requisite_courses (list): List containing prerequisite courses
        is_locked (bool): Flag to indicate if any course is locked
        status (str): Contains status of a course

    Returns:
        is_locked (bool): Flag to indicate if any course is locked
        status (str): Contains status of a course
        message (str): Message to indicate the user to pass the prerequisite courses
    """
    message = LOCKED_COURSE_MESSAGE

    for prereq in pre_requisite_courses:
        course_grade = CourseGradeFactory().read(user, course_key=prereq['key'])

        if not (course_grade and course_grade.passed):
            is_locked = True
            status = LOCKED

            course_overview = CourseOverview.objects.get(id=prereq['key'])
            message = f'{message} {course_overview.display_name_with_default},'

    message = _(f'{message[:-1]}.')

    return is_locked, status, message


def get_information_for_unlocked_course(user, course, is_any_course_started, grade):
    """
    Creates course card information based on whether the user has enrolled in the course, completed the course or failed
    the course.

    Arguments:
        user (User): User object
        course (Course):  Course for which card information is to be created
        is_any_course_started (bool): Flag to indicate if any course has been started yet
        grade (str): Grade attained in a course

    Returns:
        is_any_course_started (bool): Flag to indicate if any course has been started yet
        status (str): Contains status of a course
        grade (str): Grade attained in a course
        message (str): Message to indicate the user to pass the prerequisite courses
    """
    message = ''
    if CourseEnrollment.is_enrolled(user, course.id):
        is_any_course_started = True
        status = IN_PROGRESS
        course_grade = CourseGradeFactory().read(user, course_key=course.id)

        if course_grade:
            if course_grade.passed:
                status = COMPLETED
                grade = _(str(int(round_away_from_zero(course_grade.percent * 100))))
            elif has_attempted_all_modules(user, course):
                status = RETAKE
                message = RETAKE_COURSE_MESSAGE
                grade = _(str(int(round_away_from_zero(course_grade.percent * 100))))
    else:
        status = NOT_STARTED

    return is_any_course_started, status, grade, message


def has_attempted_all_modules(user, course):
    """
    Checks if all sections of a course have been attempted by the user or not

    Arguments:
        user (User): User object
        course (Course): Course object

    Returns:
        boolean: True if user attempted all sections, False otherwise
    """
    all_modules = modulestore().get_items(
        course.id,
        qualifiers={'category': 'course'}
    )

    modules = all_modules[0].children
    return StudentModule.objects.filter(student=user, module_state_key__in=modules).count() == len(modules)


def get_application_hub_instructions(
    user_application_hub, is_any_prerequisite_started, is_any_business_line_course_started
):
    """
    Decides congratulation messages and instructions based on the requirements completed and if courses have been
    started or not.

    Arguments:
        user_application_hub (ApplicationHub): ApplicationHub object
        is_any_prerequisite_started (bool): Flag to indicate if any prerequisite course has been started yet
        is_any_business_line_course_started (bool): Flag to indicate if any business line course has been started yet

    Returns:
        dict: Dictionary containing congratulations messages and instructions
    """
    congrats = message = instruction = ''

    if user_application_hub.are_application_pre_reqs_completed():
        congrats = APPLICATION_SUBMISSION_CONGRATS
        message = APPLICATION_SUBMISSION_INSTRUCTION

    elif user_application_hub.is_prerequisite_courses_passed:
        if is_any_business_line_course_started:
            instruction = PREREQUISITE_COURSES_COMPLETION_INSTRUCTION

        else:
            congrats = PREREQUISITE_COURSES_COMPLETION_CONGRATS
            message = PREREQUISITE_COURSES_COMPLETION_MSG

    elif user_application_hub.is_written_application_completed:
        if is_any_prerequisite_started:
            instruction = WRITTEN_APPLICATION_COMPLETION_INSTRUCTION

        else:
            congrats = WRITTEN_APPLICATION_COMPLETION_CONGRATS
            message = WRITTEN_APPLICATION_COMPLETION_MSG

    return {
        'congrats': congrats,
        'message': message,
        'instruction': instruction
    }

"""
Constants for all the tests.
"""
from datetime import date

from dateutil.relativedelta import relativedelta
from django.urls import reverse

ADMIN_TYPE_SUPER_ADMIN = 'super_admin'
ADMIN_TYPE_ADG_ADMIN = 'adg_admin'

TITLE_BUSINESS_LINE_1 = 'test_business_line1'
TITLE_BUSINESS_LINE_2 = 'test_business_line2'

USERNAME = 'test'
EMAIL = 'test@example.com'
PASSWORD = 'edx'

NOTE = 'Test note'
LINKED_IN_URL = 'Test LinkedIn URL'

ALL_FIELDSETS = (
    'preliminary_info_fieldset', 'applicant_info_fieldset', 'resume_cover_letter_fieldset', 'scores_fieldset'
)

FIELDSETS_WITHOUT_RESUME_OR_COVER_LETTER = (ALL_FIELDSETS[0], ALL_FIELDSETS[1], ALL_FIELDSETS[3])

TEST_RESUME = 'Test Resume'
TEST_COVER_LETTER_FILE = 'Test Cover Letter File'
TEST_COVER_LETTER_TEXT = 'Test Cover Letter Text'

FORMSET = 'test_formset'

COVER_LETTER_REDIRECT_URL = '{register}?next={next}'.format(
    register=reverse('register_user'),
    next=reverse('application_cover_letter')
)
MOCK_FILE_PATH = 'dummy_file.pdf'

TEST_MESSAGE_FOR_APPLICANT = 'Test message for the applicant'

VALID_USER_BIRTH_DATE_FOR_APPLICATION = date.today() - relativedelta(years=30)

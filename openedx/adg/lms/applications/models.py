"""
All models for applications app
"""
from collections import namedtuple
from datetime import date

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from openedx.adg.lms.utils.date_utils import month_choices
from lms.djangoapps.grades.api import CourseGradeFactory
from openedx.adg.common.course_meta.models import CourseMeta
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from .constants import ALLOWED_LOGO_EXTENSIONS
from .helpers import max_year_value_validator, min_year_value_validator, validate_logo_size


class ApplicationHub(TimeStampedModel):
    """
    Model for status of all required parts of user application submission.
    """

    TOTAL_APPLICATION_OBJECTIVES = 2

    user = models.OneToOneField(
        User, related_name='application_hub', on_delete=models.CASCADE, verbose_name=_('User'),
    )
    is_prerequisite_courses_passed = models.BooleanField(default=False, verbose_name=_('Prerequisite Courses Passed'), )
    is_written_application_completed = models.BooleanField(default=False,
                                                           verbose_name=_('Written Application Submitted'), )
    is_application_submitted = models.BooleanField(default=False, verbose_name=_('Application Submitted'), )
    submission_date = models.DateField(null=True, blank=True, verbose_name=_('Submission Date'), )

    class Meta:
        app_label = 'applications'

    def set_is_prerequisite_courses_passed(self):
        """
        Mark pre_req_course objective as complete i.e set is_prerequisite_courses_passed to True.
        """
        self.is_prerequisite_courses_passed = True
        self.save()

    def set_is_written_application_completed(self):
        """
        Mark written_application objective as complete i.e set is_written_application_completed to True.
        """
        self.is_written_application_completed = True
        self.save()

    def are_application_pre_reqs_completed(self):
        """
        Check if all the application objectives are completed or not.

        Returns:
            bool: True if all objectives are done, otherwise False.
        """
        return self.is_prerequisite_courses_passed and self.is_written_application_completed

    @property
    def progress_of_objectives_completed_in_float(self):
        """
        Property to return percentage of the total objectives completed.

        Returns:
            str: percentage in string
        """
        number_of_objectives_completed = sum([self.is_written_application_completed,
                                              self.is_prerequisite_courses_passed])
        return number_of_objectives_completed / self.TOTAL_APPLICATION_OBJECTIVES

    def submit_application_for_current_date(self):
        """
        Set the is_application_submitted flag and add the submission_date of the current date.
        """
        self.is_application_submitted = True
        self.submission_date = date.today()
        self.save()

    def __str__(self):
        return 'User {user_id}, application status id={id}'.format(user_id=self.user.id, id=self.id)


class BusinessLine(TimeStampedModel):
    """
    Model to save the business lines
    """

    title = models.CharField(verbose_name=_('Title'), max_length=150, unique=True, )
    logo = models.ImageField(
        upload_to='business-lines/logos/', verbose_name=_('Logo'),
        validators=[FileExtensionValidator(ALLOWED_LOGO_EXTENSIONS), validate_logo_size],
        help_text=_('Accepted extensions: .png, .jpg, .svg'),
    )
    description = models.TextField(verbose_name=_('Description'), )

    class Meta:
        app_label = 'applications'

    def __str__(self):
        return '{}'.format(self.title)


class UserApplication(TimeStampedModel):
    """
    Model for status of all required parts of user application submission.
    """

    user = models.OneToOneField(User, related_name='application', on_delete=models.CASCADE, verbose_name=_('User'), )
    business_line = models.ForeignKey(BusinessLine, verbose_name=_('Business Line'),
                                      on_delete=models.CASCADE, null=True)

    organization = models.CharField(verbose_name=_('Organization'), max_length=255, blank=True, )
    linkedin_url = models.URLField(verbose_name=_('LinkedIn URL'), max_length=255, blank=True, )
    resume = models.FileField(
        max_length=500, blank=True, null=True, upload_to='files/resume/', verbose_name=_('Resume File'),
        validators=[FileExtensionValidator(['pdf', 'doc', 'jpg', 'png'])],
        help_text=_('Accepted extensions: .pdf, .doc, .jpg, .png'),
    )
    cover_letter_file = models.FileField(
        max_length=500, blank=True, null=True, upload_to='files/cover_letter/', verbose_name=_('Cover Letter File'),
        validators=[FileExtensionValidator(['pdf', 'doc', 'jpg', 'png'])],
        help_text=_('Accepted extensions: .pdf, .doc, .jpg, .png'),
    )
    cover_letter = models.TextField(blank=True, verbose_name=_('Cover Letter'), )

    OPEN = 'open'
    ACCEPTED = 'accepted'
    WAITLIST = 'waitlist'

    STATUS_CHOICES = (
        (OPEN, _('Open')),
        (ACCEPTED, _('Accepted')),
        (WAITLIST, _('Waitlist')),
    )
    status = models.CharField(
        verbose_name=_('Application Status'), choices=STATUS_CHOICES, max_length=8, default=OPEN,
    )
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_('Reviewed By')
    )
    internal_admin_note = models.TextField(null=True, blank=True, verbose_name=_('Admin Note'))

    class Meta:
        app_label = 'applications'
        verbose_name = _('Application')
        ordering = ['created']

    def __str__(self):
        return '{}'.format(self.user.profile.name)  # pylint: disable=E1101

    @property
    def cover_letter_provided(self):
        return self.cover_letter or self.cover_letter_file

    @property
    def cover_letter_and_resume(self):
        return self.cover_letter_provided and self.resume

    @property
    def cover_letter_or_resume(self):
        return self.cover_letter_provided or self.resume

    @property
    def file_attached(self):
        return self.resume or self.cover_letter_file

    @property
    def prereq_course_scores(self):
        """
        Fetch and return applicant scores in the pre-requisite courses of the franchise program.

        Returns:
            list: Prereq course name and score pairs
        """
        prereq_course_overviews = CourseOverview.objects.filter(id__in=CourseMeta.prereq_course_ids.all())

        CourseScore = namedtuple('CourseScore', 'course_name course_percentage')
        scores_in_prereq_courses = []

        for course_overview in prereq_course_overviews:
            course_name = course_overview.display_name
            course_grade = CourseGradeFactory().read(self.user, course_key=course_overview.id)
            course_percentage = course_grade.percent*100

            course_score = CourseScore(course_name, course_percentage)
            scores_in_prereq_courses.append(course_score)

        return scores_in_prereq_courses

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        if self.pk:
            current = UserApplication.objects.get(pk=self.pk)
            if current.resume != self.resume:
                current.resume.delete(save=False)
            if current.cover_letter_file != self.cover_letter_file:
                current.cover_letter_file.delete(save=False)
        super(UserApplication, self).save(*args, **kwargs)


class UserStartAndEndDates(TimeStampedModel):
    """
    An abstract model for start and end dates.
    """

    month_choices = month_choices(default_title='Month')

    user_application = models.ForeignKey(
        'UserApplication', related_name='%(app_label)s_%(class)ss', related_query_name='%(app_label)s_%(class)s',
        on_delete=models.CASCADE,
    )
    date_started_month = models.IntegerField(verbose_name=_('Start Month'), choices=month_choices, )
    date_completed_month = models.IntegerField(
        verbose_name=_('Completed Month'), choices=month_choices, blank=True, null=True,
    )
    date_started_year = models.IntegerField(
        verbose_name=_('Start Year'),
        validators=(min_year_value_validator, max_year_value_validator)
    )
    date_completed_year = models.IntegerField(
        verbose_name=_('Completed Year'), blank=True, null=True,
        validators=(min_year_value_validator, max_year_value_validator)
    )

    class Meta(object):
        abstract = True


class Education(UserStartAndEndDates):
    """
    Model for user education qualification for application submission.
    """

    HIGH_SCHOOL_DIPLOMA = 'HD'
    ASSOCIATE_DEGREE = 'AD'
    BACHELOR_DEGREE = 'BD'
    MASTERS_DEGREE = 'MD'
    DOCTORAL_DEGREE = 'DD'

    DEGREE_TYPES = [
        (HIGH_SCHOOL_DIPLOMA, _('High School Diploma or GED')),
        (ASSOCIATE_DEGREE, _('Associate Degree')),
        (BACHELOR_DEGREE, _('Bachelor’s Degree')),
        (MASTERS_DEGREE, _('Master’s Degree')),
        (DOCTORAL_DEGREE, _('Doctoral Degree')),
    ]

    name_of_school = models.CharField(verbose_name=_('School / University'), max_length=255, )
    degree = models.CharField(verbose_name=_('Degree Received'), choices=DEGREE_TYPES, max_length=2, )
    area_of_study = models.CharField(verbose_name=_('Area of Study'), max_length=255, blank=True, )
    is_in_progress = models.BooleanField(verbose_name=_('In Progress'), default=False, )

    class Meta:
        app_label = 'applications'

    def __str__(self):
        return ''


class WorkExperience(UserStartAndEndDates):
    """
    Model for user work experience for application submission.
    """

    name_of_organization = models.CharField(verbose_name=_('Organization'), max_length=255, )
    job_position_title = models.CharField(verbose_name=_('Job Position / Title'), max_length=255, )
    is_current_position = models.BooleanField(verbose_name=_('Current Position'), default=False, )
    job_responsibilities = models.TextField(verbose_name=_('Job Responsibilities'), )

    class Meta:
        app_label = 'applications'

    def __str__(self):
        return ''

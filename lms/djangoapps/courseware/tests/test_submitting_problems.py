# -*- coding: utf-8 -*-
"""
Integration tests for submitting problem responses and getting grades.
"""

# pylint: disable=attribute-defined-outside-init


import json
import os
from textwrap import dedent

import ddt
import six
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connections
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.timezone import now
from mock import patch
from six import text_type
from submissions import api as submissions_api

from capa.tests.response_xml_factory import (
    CodeResponseXMLFactory,
    CustomResponseXMLFactory,
    OptionResponseXMLFactory,
    SchematicResponseXMLFactory
)
from common.djangoapps.course_modes.models import CourseMode
from lms.djangoapps.courseware.models import BaseStudentModuleHistory, StudentModule
from lms.djangoapps.courseware.tests.helpers import LoginEnrollmentTestCase
from lms.djangoapps.grades.api import CourseGradeFactory, task_compute_all_grades_for_course
from openedx.core.djangoapps.credit.api import get_credit_requirement_status, set_credit_requirements
from openedx.core.djangoapps.credit.models import CreditCourse, CreditProvider
from openedx.core.djangoapps.user_api.tests.factories import UserCourseTagFactory
from openedx.core.lib.url_utils import quote_slashes
from common.djangoapps.student.models import CourseEnrollment, anonymous_id_for_user
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.partitions.partitions import Group, UserPartition


class ProblemSubmissionTestMixin(TestCase):
    """
    TestCase mixin that provides functions to submit answers to problems.
    """
    def refresh_course(self):
        """
        Re-fetch the course from the database so that the object being dealt with has everything added to it.
        """
        self.course = self.store.get_course(self.course.id)

    def problem_location(self, problem_url_name):
        """
        Returns the url of the problem given the problem's name
        """
        return self.course.id.make_usage_key('problem', problem_url_name)

    def modx_url(self, problem_location, dispatch):
        """
        Return the url needed for the desired action.

        problem_location: location of the problem on which we want some action

        dispatch: the the action string that gets passed to the view as a kwarg
            example: 'check_problem' for having responses processed
        """
        return reverse(
            'xblock_handler',
            kwargs={
                'course_id': text_type(self.course.id),
                'usage_id': quote_slashes(text_type(problem_location)),
                'handler': 'xmodule_handler',
                'suffix': dispatch,
            }
        )

    def submit_question_answer(self, problem_url_name, responses):
        """
        Submit answers to a question.

        Responses is a dict mapping problem ids to answers:
            {'2_1': 'Correct', '2_2': 'Incorrect'}
        """

        problem_location = self.problem_location(problem_url_name)
        modx_url = self.modx_url(problem_location, 'problem_check')

        answer_key_prefix = 'input_{}_'.format(problem_location.html_id())

        # format the response dictionary to be sent in the post request by adding the above prefix to each key
        response_dict = {(answer_key_prefix + k): v for k, v in responses.items()}
        resp = self.client.post(modx_url, response_dict)

        return resp

    def look_at_question(self, problem_url_name):
        """
        Create state for a problem, but don't answer it
        """
        location = self.problem_location(problem_url_name)
        modx_url = self.modx_url(location, "problem_get")
        resp = self.client.get(modx_url)
        return resp

    def reset_question_answer(self, problem_url_name):
        """
        Reset specified problem for current user.
        """
        problem_location = self.problem_location(problem_url_name)
        modx_url = self.modx_url(problem_location, 'problem_reset')
        resp = self.client.post(modx_url)
        return resp

    def rescore_question(self, problem_url_name):
        """
        Reset specified problem for current user.
        """
        problem_location = self.problem_location(problem_url_name)
        modx_url = self.modx_url(problem_location, 'problem_reset')
        resp = self.client.post(modx_url)
        return resp

    def show_question_answer(self, problem_url_name):
        """
        Shows the answer to the current student.
        """
        problem_location = self.problem_location(problem_url_name)
        modx_url = self.modx_url(problem_location, 'problem_show')
        resp = self.client.post(modx_url)
        return resp

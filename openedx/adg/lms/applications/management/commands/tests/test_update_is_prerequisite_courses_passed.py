"""
Tests to check if update_is_prerequisite_courses_passed command
actually updates the is_prerequisite_courses_passed flag in
Application Hub for each eligible user
"""

from datetime import datetime

import pytest
from django.core.management import call_command

from openedx.adg.common.course_meta.factory import CourseMetaFactory
from openedx.adg.common.course_meta.models import CourseMeta
from openedx.adg.lms.applications.management.commands import update_is_prerequisite_courses_passed as command_module
from openedx.adg.lms.applications.models import ApplicationHub
from openedx.core.djangoapps.content.course_overviews.tests.factories import CourseOverviewFactory
from student.tests.factories import CourseEnrollmentFactory, UserFactory


@pytest.fixture
def user_for_testing(request):
    return UserFactory.create()


@pytest.fixture
def course_for_testing(request):
    prerequisite_course = CourseOverviewFactory.create(
        end_date=datetime(2022, 1, 1),
        start_date=datetime(2015, 1, 1),
        display_name='pre requisite course'
    )

    CourseMetaFactory(course=prerequisite_course)

    return prerequisite_course


@pytest.fixture
def enroll_user(request, user_for_testing, course_for_testing):
    CourseEnrollmentFactory.create(
        user=user_for_testing,
        course_id=course_for_testing.id,
        is_active=request.param['is_active']
    )


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': False})],
                         indirect=True)
def test_minimal_users_with_inactive_user(enroll_user):
    pre_req_courses = CourseMeta.open_pre_req_courses.all()

    command = command_module.Command()
    minimal_users = command.get_minimal_users_to_be_checked_for_update(
        pre_req_courses)

    assert minimal_users.count() == 0


@pytest.mark.django_db
def test_minimal_users_none_registered_in_prerequisite(course_for_testing):
    pre_req_courses = CourseMeta.open_pre_req_courses.all()

    command = command_module.Command()
    minimal_users = command.get_minimal_users_to_be_checked_for_update(
        pre_req_courses)

    assert minimal_users.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': True})],
                         indirect=True)
def test_minimal_users(enroll_user):
    pre_req_courses = CourseMeta.open_pre_req_courses.all()

    command = command_module.Command()
    minimal_users = command.get_minimal_users_to_be_checked_for_update(
        pre_req_courses)

    assert minimal_users.count() > 0


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': True})],
                         indirect=True)
def test_user_failed_in_course(user_for_testing, enroll_user):
    pre_req_courses = CourseMeta.open_pre_req_courses.all()

    command = command_module.Command()
    flag = command.is_user_failed_in_course(user_for_testing,
                                            pre_req_courses.first())

    assert flag == True


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': True})],
                         indirect=True)
def test_user_passed_in_course(mocker, user_for_testing, enroll_user):
    mocker.patch(
        'lms.djangoapps.grades.course_grade_factory.CourseGradeFactory._read')

    class MockClass:
        passed = True

    mocker.return_value = MockClass()

    pre_req_courses = CourseMeta.open_pre_req_courses.all()

    command = command_module.Command()
    flag = command.is_user_failed_in_course(user_for_testing,
                                            pre_req_courses.first())

    assert flag == False


@pytest.mark.django_db
def test_handle_with_no_prerequisites():
    with pytest.raises(SystemExit) as wrapped_exception:
        call_command('update_is_prerequisite_courses_passed')

    assert wrapped_exception.type == SystemExit


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': False})],
                         indirect=True)
def test_handle_with_no_minimal_user(user_for_testing, enroll_user):

    call_command('update_is_prerequisite_courses_passed')

    user_application_hub, _ = ApplicationHub.objects.get_or_create(
        user=user_for_testing)

    assert user_application_hub.is_prerequisite_courses_passed == False


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': True})],
                         indirect=True)
def test_handle_with_user_failed(user_for_testing, enroll_user):

    call_command('update_is_prerequisite_courses_passed')

    user_application_hub, _ = ApplicationHub.objects.get_or_create(
        user=user_for_testing)

    assert user_application_hub.is_prerequisite_courses_passed == False


@pytest.mark.django_db
@pytest.mark.parametrize('enroll_user',
                         [dict({'is_active': True})],
                         indirect=True)
def test_handle_with_user_passed(mocker, user_for_testing, enroll_user):
    mocker.patch.object(command_module.CourseGradeFactory, '_read')

    class MockClass:
        passed = True

    mocker.return_value = MockClass()

    call_command('update_is_prerequisite_courses_passed')

    user_application_hub, _ = ApplicationHub.objects.get_or_create(
        user=user_for_testing)

    assert user_application_hub.is_prerequisite_courses_passed == True

"""
Tests for all the views in applications app.
"""
from datetime import date

import mock
import pytest
from django.test import Client, RequestFactory
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND, HTTP_400_BAD_REQUEST

from common.djangoapps.student.tests.factories import UserFactory
from openedx.adg.lms.applications.views import (
    ApplicationHubView,
    ApplicationIntroductionView,
    ApplicationSuccessView,
    BusinessLineInterestView,
    ContactInformationView,
    EducationAndExperienceView
)
from openedx.adg.lms.registration_extension.tests.factories import ExtendedUserProfileFactory

from .constants import (
    BUSINESS_LINE_INTEREST_REDIRECT_URL,
    PASSWORD,
    TEST_BACKGROUND_QUESTION,
    TEST_INTEREST_IN_BUSINESS,
    USERNAME,
    VALID_USER_BIRTH_DATE_FOR_APPLICATION
)
from .factories import ApplicationHubFactory, BusinessLineFactory, EducationFactory, UserApplicationFactory


@pytest.mark.django_db
@pytest.fixture(name='user')
def user_fixture():
    """
    Create a test user and their corresponding ApplicationHub object

    Returns:
        User object
    """
    user = UserFactory(username=USERNAME, password=PASSWORD)
    ApplicationHubFactory(user=user)
    ExtendedUserProfileFactory(user=user)
    return user


@pytest.fixture(scope='module', name='request_factory')
def request_factory_fixture():
    """
    Returns the request factory to make requests.

    Returns:
         RequestFactory object
    """
    return RequestFactory()


@pytest.fixture(name='application_hub_view_get_request')
def application_hub_view_get_request_fixture(request_factory, user):
    """
    Return a HttpRequest object for application hub get

    Args:
        request_factory (RequestFactory): factory to make requests
        user (User): The user that is logged in

    Returns:
        HttpRequest object
    """
    request = request_factory.get(reverse('application_hub'))
    request.user = user
    return request


@pytest.fixture(name='logged_in_client')
def logged_in_client_fixture(user):
    """
    Return a logged in client

    Args:
        user (User): user to log in

    Returns:
        Client() object with logged in user
    """
    client = Client()
    client.login(username=user.username, password=PASSWORD)
    return client


# ------- Application Introduction View tests below -------


@pytest.mark.django_db
def test_get_redirects_without_login_for_application_introduction_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_introduction_url = reverse('application_introduction')
    response = Client().get(application_introduction_url)
    assert f'/register?next={application_introduction_url}' == response.url


@pytest.mark.django_db
@pytest.mark.parametrize('application_hub, status_code, expected_output', [
    (True, HTTP_302_FOUND, reverse('application_hub')),
    (False, HTTP_200_OK, None)
])
def test_application_introduction_view_for_logged_in_user(
    application_hub, status_code, expected_output, request_factory, mocker
):
    """
    Test that Application Introduction view is only accessible to users that have no ApplicationHub object i.e have not
    clicked the `Start Application` button on Application Introduction page
    """
    mocker.patch('openedx.adg.lms.applications.views.render')

    test_user = UserFactory()
    request = request_factory.get(reverse('application_introduction'))
    request.user = test_user

    if application_hub:
        ApplicationHubFactory(user=test_user)

    response = ApplicationIntroductionView.as_view()(request)
    assert response.get('Location') == expected_output
    assert response.status_code == status_code


# ------- Application Hub View tests below -------


@pytest.mark.django_db
def test_get_redirects_without_login_for_application_hub_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_hub_url = reverse('application_hub')
    response = Client().get(application_hub_url)
    assert f'/login?next={application_hub_url}' == response.url


@pytest.mark.django_db
def test_post_user_redirects_without_login_for_application_hub_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_hub_url = reverse('application_hub')
    response = Client().post(application_hub_url)
    assert f'/login?next={application_hub_url}' == response.url


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.render')
def test_get_initial_application_state_for_application_hub_view(mock_render, application_hub_view_get_request):
    """
    Test the case where the user has not completed even a single objective of the application.
    """
    ApplicationHubView.as_view()(application_hub_view_get_request)

    expected_context = {
        'user_application_hub': application_hub_view_get_request.user.application_hub,
        'pre_req_courses': []
    }
    mock_render.assert_called_once_with(
        application_hub_view_get_request, 'adg/lms/applications/hub.html', context=expected_context
    )


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.render')
def test_get_written_application_completed_state_for_application_hub_view(
    mock_render, application_hub_view_get_request
):
    """
    Test the case where the user has completed the written application but not the pre_req courses.
    """
    ApplicationHubView.as_view()(application_hub_view_get_request)

    expected_context = {
        'user_application_hub': application_hub_view_get_request.user.application_hub,
        'pre_req_courses': []
    }
    mock_render.assert_called_once_with(
        application_hub_view_get_request, 'adg/lms/applications/hub.html', context=expected_context
    )


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.render')
def test_get_pre_req_courses_passed_state_for_application_hub_view(mock_render, application_hub_view_get_request):
    """
    Test the case where the user has completed the pre_req courses but not the written application.
    """
    ApplicationHubView.as_view()(application_hub_view_get_request)

    user = application_hub_view_get_request.user
    user.application_hub.set_is_prerequisite_courses_passed()
    expected_context = {
        'user_application_hub': user.application_hub,
        'pre_req_courses': []
    }
    mock_render.assert_called_once_with(
        application_hub_view_get_request, 'adg/lms/applications/hub.html', context=expected_context
    )


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.render')
def test_get_complete_application_done_state_for_application_hub_view(mock_render, application_hub_view_get_request):
    """
    Test the case where the user has completed both objectives i.e the pre_req courses and the
    written application.
    """
    ApplicationHubView.as_view()(application_hub_view_get_request)

    expected_context = {
        'user_application_hub': application_hub_view_get_request.user.application_hub,
        'pre_req_courses': []
    }
    mock_render.assert_called_once_with(
        application_hub_view_get_request, 'adg/lms/applications/hub.html', context=expected_context
    )


@pytest.mark.django_db
def test_get_already_submitted_application_state_for_application_hub_view(application_hub_view_get_request):
    """
    Test the case where the user does not even have a corresponding application.
    """
    application_hub_view_get_request.user.application_hub.submit_application_for_current_date()

    response = ApplicationHubView.as_view()(application_hub_view_get_request)
    assert response.get('Location') == reverse('application_success')
    assert response.status_code == HTTP_302_FOUND


@pytest.mark.django_db
def test_post_logged_in_user_without_required_objectives_completed_for_application_hub_view(logged_in_client):
    """
    Test the case where an authenticated user hits the url without having completed the required objectives i.e
    the pre_req courses and the written application.
    """
    response = logged_in_client.post(reverse('application_hub'))
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.send_application_submission_confirmation_email')
def test_post_logged_in_user_with_required_objectives_completed_to_application_hub_view(
    mock_send_mail, user, logged_in_client
):
    """
    Test the case where an authenticated user, with all the required objectives completed, hits the url.
    """
    user.application_hub.set_is_prerequisite_courses_passed()
    user.application_hub.submit_written_application_for_current_date()

    response = logged_in_client.post(reverse('application_hub'))
    assert mock_send_mail.called
    assert ApplicationHubFactory(user=user).is_application_submitted
    assert ApplicationHubFactory(user=user).submission_date == date.today()
    assert response.get('Location') == reverse('application_success')
    assert response.status_code == HTTP_302_FOUND


@pytest.mark.django_db
def test_post_already_submitted_application_to_application_hub_view(user, logged_in_client):
    """
    Test the case where a user with already submitted application hits the url again.
    """
    user.application_hub.set_is_prerequisite_courses_passed()
    user.application_hub.submit_written_application_for_current_date()
    user.application_hub.submit_application_for_current_date()

    response = logged_in_client.post(reverse('application_hub'))
    assert response.status_code == HTTP_302_FOUND
    assert response.get('Location') == reverse('application_success')


# ------- Application Success View tests below -------


@pytest.fixture(name='get_request_for_application_success_view')
def get_request_for_application_success_view_fixture(request_factory, user):
    """
    Create a get request for the application_success url.
    """
    request = request_factory.get(reverse('application_success'))
    request.user = user
    return request


@pytest.mark.django_db
def test_get_environment_in_context_for_application_success_view(get_request_for_application_success_view):
    """
    Test if the context contains all the necessary pieces.
    """
    get_request_for_application_success_view.user.application_hub.submit_application_for_current_date()

    response = ApplicationSuccessView.as_view()(get_request_for_application_success_view)
    assert 'submission_date' in response.context_data


@pytest.mark.django_db
def test_get_unauthenticated_user_redirects_for_application_success_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_success_url = reverse('application_success')
    response = Client().get(application_success_url)
    assert f'/login?next={application_success_url}' in response.url


@pytest.mark.django_db
def test_get_submission_date_for_application_success_view(get_request_for_application_success_view):
    """
    Test if the right date is being fed to the context dictionary.
    """
    user_application_hub = get_request_for_application_success_view.user.application_hub
    user_application_hub.submit_application_for_current_date()

    response = ApplicationSuccessView.as_view()(get_request_for_application_success_view)
    assert response.context_data.get('submission_date') == user_application_hub.submission_date
    assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_get_user_without_submitted_application_for_application_success_view(logged_in_client):
    """
    Test the case where a user has not submitted their application.
    """
    response = logged_in_client.get(reverse('application_success'))
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_get_no_user_application_exists_for_application_success_view(get_request_for_application_success_view):
    """
    Test the case where a user does not have an associated ApplicationHub object.
    """
    get_request_for_application_success_view.user.application_hub = None

    response = ApplicationSuccessView.as_view()(get_request_for_application_success_view)
    assert response.status_code == HTTP_400_BAD_REQUEST


# ------- Contact Information View tests below -------


@pytest.fixture(name='get_request_for_contact_information_view')
def get_request_for_contact_information_view_fixture(request_factory, user):
    """
    Create a get request for the contact_information url.
    """
    request = request_factory.get(reverse('application_contact'))
    request.user = user
    return request


@pytest.fixture(name='post_request_for_contact_information_view')
def post_request_for_contact_information_view_fixture(request_factory, user):
    """
    Create a get request for the contact_information url.
    """
    request = request_factory.post(reverse('application_contact'))
    request.user = user
    return request


@pytest.mark.django_db
def test_get_redirects_without_login_for_contact_information_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_contact_url = reverse('application_contact')
    response = Client().get(application_contact_url)
    assert f'/register?next={application_contact_url}' == response.url


@pytest.mark.django_db
def test_post_user_redirects_without_login_for_contact_information_view():
    """
    Test the case where an unauthenticated user is redirected to login page or not.
    """
    application_contact_url = reverse('application_contact')
    response = Client().post(application_contact_url)
    assert f'/register?next={application_contact_url}' == response.url


@pytest.mark.django_db
def test_get_already_submitted_application_to_contact_information_view(get_request_for_contact_information_view):
    """
    Test the case where a user with already submitted application hits the url again.
    """
    request = get_request_for_contact_information_view
    request.user.application_hub.submit_written_application_for_current_date()
    response = ContactInformationView.as_view()(request)
    assert response.get('Location') == reverse('application_hub')


@pytest.mark.django_db
def test_post_already_submitted_application_to_contact_information_view(post_request_for_contact_information_view):
    """
    Test the case where a user with already submitted application hits the url again.
    """
    request = post_request_for_contact_information_view
    request.user.application_hub.submit_written_application_for_current_date()
    response = ContactInformationView.as_view()(request)
    assert response.status_code == HTTP_400_BAD_REQUEST


# ------- Education & Experience View tests below -------


@pytest.fixture(name='prereqs_completed_education_experience_view')
def education_experience_view_prereqs_completed(user):
    """
    All the required prereqs to access the education experience view
    """
    user.application_hub.is_written_application_completed = False
    UserApplicationFactory(user=user)
    user.extended_profile.saudi_national = True
    user.extended_profile.birth_date = VALID_USER_BIRTH_DATE_FOR_APPLICATION


@pytest.mark.django_db
def test_get_redirects_without_login_for_education_experience_view():
    """
    Test the case where an unauthenticated user is redirected to register page or not.
    """
    response = Client().get(reverse('application_education_experience'))
    assert reverse('register_user') in response.url


@pytest.mark.django_db
def test_education_experience_view_without_application_hub(user, logged_in_client):
    """
    Test education experience view if application hub is not created for user
    """
    user.application_hub.delete()
    response = logged_in_client.get(reverse('application_education_experience'))
    assert reverse('application_hub') in response.url


@pytest.mark.parametrize('is_written_app_completed, has_user_application, is_saudi, has_birthdate, will_redirect', [
    (True, True, True, True, True),
    (False, False, True, True, True),
    (False, True, False, True, True),
    (False, True, True, False, True),
    (False, False, False, True, True),
    (False, False, True, False, True),
    (False, True, False, False, True),
    (False, True, True, True, False)
], ids=[
    'written_app_completed',
    'written_app_not_completed_with_no_application',
    'written_app_not_completed_and_is_not_saudi',
    'written_app_not_completed_and_has_no_birthdate',
    'written_app_not_completed_with_no_application_and_is_not_saudi',
    'written_app_not_completed_with_no_application_and_has_no_birthdate',
    'written_app_not_completed_and_is_not_saudi_and_has_no_birthdate',
    'written_app_not_completed_with_application_and_is_saudi_and_has_birthdate'
])
@pytest.mark.django_db
def test_get_with_or_without_required_prereqs_completed_education_experience_view(
    request_factory,
    user,
    mocker,
    is_written_app_completed,
    has_user_application,
    is_saudi,
    has_birthdate,
    will_redirect
):
    """
    Test that if a user tries to get the education & experience page with incomplete prereqs
    e.g written application already submitted, not a saudi, has no user application etc, the user
    should be redirected to application hub page. The user is only allowed to visit the url with
    complete required data added from the previous step of the application i.e Contact Info page
    """
    mock_render = mocker.patch('openedx.adg.lms.applications.views.render')

    user.application_hub.is_written_application_completed = is_written_app_completed
    if has_user_application:
        UserApplicationFactory(user=user)
    user.extended_profile.saudi_national = is_saudi
    user.extended_profile.birth_date = VALID_USER_BIRTH_DATE_FOR_APPLICATION if has_birthdate else None

    request = request_factory.get(reverse('application_education_experience'))
    request.user = user

    response = EducationAndExperienceView.as_view()(request)

    if will_redirect:
        assert response.get('Location') == reverse('application_hub')
        assert response.status_code == HTTP_302_FOUND
    else:
        mock_render.assert_called_with(request, 'adg/lms/applications/education_experience.html', mock.ANY)


@pytest.mark.django_db
@pytest.mark.parametrize('is_written_app_completed, has_user_application, is_saudi, has_birthdate', [
    (True, True, True, True),
    (False, False, True, True),
    (False, True, False, True),
    (False, True, True, False),
    (False, False, False, True),
    (False, False, True, False),
    (False, True, False, False)
], ids=[
    'written_app_completed',
    'written_app_not_completed_with_no_application',
    'written_app_not_completed_and_is_not_saudi',
    'written_app_not_completed_and_has_no_birthdate',
    'written_app_not_completed_with_no_application_and_is_not_saudi',
    'written_app_not_completed_with_no_application_and_has_no_birthdate',
    'written_app_not_completed_and_is_not_saudi_and_has_no_birthdate'
])
def test_post_without_required_prereqs_completed_education_experience_view(
    is_written_app_completed, has_user_application, is_saudi, has_birthdate, logged_in_client, user
):
    """
    Test that if a user tries to do a post request to the education_experience page with incomplete
    prereqs e.g no education added, no work added etc, the user must be returned with status 400.
    """
    user.application_hub.is_written_application_completed = is_written_app_completed
    if has_user_application:
        UserApplicationFactory(user=user)
    user.extended_profile.saudi_national = is_saudi
    user.extended_profile.birth_date = VALID_USER_BIRTH_DATE_FOR_APPLICATION if has_birthdate else None

    response = logged_in_client.post(reverse('application_education_experience'))
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    'button, background_question, template',
    [
        ('back', TEST_BACKGROUND_QUESTION, 'application_contact'),
        ('back', '', 'application_contact'),
        ('next', TEST_BACKGROUND_QUESTION, 'application_business_line_interest')
    ],
    ids=['back_with_background_question', 'back_with_no_background_question', 'next_with_background_question']
)
# pylint: disable=unused-argument, protected-access
def test_post_back_or_next_with_required_data_education_experience_view(
    request_factory, user, education, prereqs_completed_education_experience_view, button, background_question, template
):
    """
    Test that the user is redirected to contact on clicking back and to business line interest
    page on clicking next when all the required data is added
    """
    request = request_factory.post(reverse('application_education_experience'))
    request.user = user

    _mutable = request.POST._mutable
    request.POST._mutable = True
    request.POST['background_question'] = background_question
    request.POST['next_or_back_clicked'] = button
    request.POST._mutable = _mutable

    response = EducationAndExperienceView.as_view()(request)

    assert response.get('Location') == reverse(template)
    assert response.status_code == HTTP_302_FOUND


@mock.patch('openedx.adg.lms.applications.views.render')
@pytest.mark.django_db
# pylint: disable=unused-argument
def test_post_without_required_data_in_education_experience_view(
    mock_render, request_factory, user, prereqs_completed_education_experience_view
):
    # pylint: disable=protected-access
    """
    Tests that when the user makes a post request in the education & experience page without adding
    the required data i.e background question, the user is not taken to a new page
    """

    request = request_factory.post(reverse('application_education_experience'))
    request.user = user

    _mutable = request.POST._mutable
    request.POST._mutable = True
    request.POST['background_question'] = ''
    request.POST['next_or_back_clicked'] = 'next'
    request.POST._mutable = _mutable

    EducationAndExperienceView.as_view()(request)
    mock_render.assert_called_once_with(request, 'adg/lms/applications/education_experience.html', mock.ANY)


# ------- Business Line Interest View tests below -------


@pytest.fixture(name='prereqs_completed_business_line_interest_view')
def business_line_interest_view_prereqs_completed(user):
    """
    All the required prereqs to access the business line view
    """
    UserApplicationFactory(user=user)
    EducationFactory(user_application=user.application)
    user.application.is_work_experience_not_applicable = True
    user.application.background_question = TEST_BACKGROUND_QUESTION


@pytest.fixture(name='business_line_interest_view_get_request')
def business_line_interest_view_get_request_fixture(request_factory, user):
    """
    Return a HttpRequest object for business line interest get request
    Args:
        request_factory (RequestFactory): factory to make requests
        user (User): The user that is logged in
    Returns:
        HttpRequest object
    """
    request = request_factory.get(reverse('application_business_line_interest'))
    request.user = user
    return request


@pytest.fixture(name='business_line_interest_view_post_request')
def business_line_interest_view_post_request_fixture(request_factory, user):
    """
    Return a HttpRequest object for business line interest post request
    Args:
        request_factory (RequestFactory): factory to make requests
        user (User): The user that is logged in
    Returns:
        HttpRequest object
    """
    request = request_factory.post(reverse('application_business_line_interest'))
    request.user = user
    return request


@pytest.mark.django_db
@pytest.mark.parametrize('is_get_request', [True, False], ids=['get_request', 'post_request'])
def test_redirection_of_a_user_without_login_for_business_line_interest_view(is_get_request):
    """
    Test if an unauthenticated user is redirected to login page on sending a get or post request.
    """
    if is_get_request:
        response = Client().get(reverse('application_business_line_interest'))
    else:
        response = Client().post(reverse('application_business_line_interest'))

    assert BUSINESS_LINE_INTEREST_REDIRECT_URL in response.url


@pytest.mark.django_db
@pytest.mark.parametrize('is_get_request', [True, False], ids=['get_request', 'post_request'])
def test_response_for_user_with_complete_written_application_business_line_interest_view(
    is_get_request, business_line_interest_view_get_request, business_line_interest_view_post_request
):
    """
    Test that if a user who has already completed written application sends a get request, they are redirected to the
    Application Hub page and if a user sends a post request, http 400 is returned.
    """
    request = business_line_interest_view_get_request if is_get_request else business_line_interest_view_post_request

    request.user.application_hub.submit_written_application_for_current_date()

    response = BusinessLineInterestView.as_view()(request)

    if is_get_request:
        assert response.get('Location') == reverse('application_hub')
        assert response.status_code == HTTP_302_FOUND
    else:
        assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@mock.patch('openedx.adg.lms.applications.views.render')
@mock.patch('openedx.adg.lms.applications.views.BusinessLine.objects.all')
@mock.patch('openedx.adg.lms.applications.views.BusinessLineInterestForm')
@pytest.mark.parametrize('has_user_application, added_work_exp, added_education, bg_question, will_redirect', [
    (False, True, True, True, True),
    (True, False, True, True, True),
    (True, True, False, True, True),
    (True, True, True, False, True),
    (True, False, False, True, True),
    (True, True, False, False, True),
    (True, False, True, False, True),
    (True, True, True, True, False)
], ids=[
    'no_application',
    'application_with_no_work',
    'application_with_no_education',
    'application_with_no_bg_question',
    'application_with_no_work_no_education',
    'application_with_no_education_no_bg_question',
    'application_with_no_work_no_bg_question',
    'application_with_work_education_bg_question'
])
def test_get_with_or_without_required_prereqs_completed_business_line_interest_view(
    mock_business_line_interest_form,
    mock_business_lines,
    mock_render,
    business_line_interest_view_get_request,
    has_user_application,
    added_work_exp,
    added_education,
    bg_question,
    will_redirect
):
    """
    Test that if a user tries to get the business line page with incomplete prereqs e.g no education
    added, no work added, no background etc, the user must be redirected to application hub page.
    The user is only allowed to visit the url with complete required data added from the previous
    step i.e Education & Experience page
    """
    mock_business_line_interest_form.return_value = 'form'
    mock_business_lines.return_value = 'business_lines'
    user = business_line_interest_view_get_request.user

    if has_user_application:
        UserApplicationFactory(user=user)
        if added_education:
            EducationFactory(user_application=user.application)
        user.application.is_work_experience_not_applicable = added_work_exp
        user.application.background_question = TEST_BACKGROUND_QUESTION if bg_question else ''

    response = BusinessLineInterestView.as_view()(business_line_interest_view_get_request)

    context = {
        'business_lines': 'business_lines',
        'application_form': 'form'
    }

    if will_redirect:
        assert response.get('Location') == reverse('application_hub')
        assert response.status_code == HTTP_302_FOUND
    else:
        mock_render.assert_called_once_with(
            business_line_interest_view_get_request, 'adg/lms/applications/business_line_interest.html', context
        )


@pytest.mark.django_db
@pytest.mark.parametrize('has_user_application, added_work_exp, added_education, bg_question', [
    (False, True, True, True),
    (True, False, True, True),
    (True, True, False, True),
    (True, True, True, False),
    (True, False, False, True),
    (True, True, False, False),
    (True, False, True, False),
], ids=[
    'no_application',
    'application_with_no_work',
    'application_with_no_education',
    'application_with_no_bg_question',
    'application_with_no_work_no_education',
    'application_with_no_education_no_bg_question',
    'application_with_no_work_no_bg_question',
]
)
def test_post_without_required_prereqs_completed_business_line_interest_view(
    logged_in_client,
    user,
    has_user_application,
    added_work_exp,
    added_education,
    bg_question,
):
    """
    Tests that if a user tries to do a post request to the business line page with incomplete prereqs
    e.g no education added, no work added, no background added etc, the user must be returned with status 400.
    """
    if has_user_application:
        UserApplicationFactory(user=user)
        if added_education:
            EducationFactory(user_application=user.application)
        user.application.is_work_experience_not_applicable = added_work_exp
        user.application.background_question = TEST_BACKGROUND_QUESTION if bg_question else ''

    response = logged_in_client.post(reverse('application_business_line_interest'))
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    'button, interest_in_business, template',
    [
        ('back', TEST_INTEREST_IN_BUSINESS, 'application_education_experience'),
        ('back', '', 'application_education_experience'),
        ('submit', TEST_INTEREST_IN_BUSINESS, 'application_hub')
    ], ids=['back_with_interest', 'back_with_no_interest', 'submit_with_interest']
)
# pylint: disable=unused-argument,protected-access
def test_post_back_or_submit_with_required_data_business_line_interest_view(
    button,
    interest_in_business,
    template,
    business_line_interest_view_post_request,
    prereqs_completed_business_line_interest_view
):
    """
    Tests that the user can post via `back` button with or without adding any interest in business
    Also tests that the user can post via `submit` button with interest in business
    """
    business_line = BusinessLineFactory()

    _mutable = business_line_interest_view_post_request.POST._mutable
    business_line_interest_view_post_request.POST._mutable = True
    business_line_interest_view_post_request.POST['business_line'] = business_line.id
    business_line_interest_view_post_request.POST['interest_in_business'] = interest_in_business
    business_line_interest_view_post_request.POST['submit_or_back_clicked'] = button
    business_line_interest_view_post_request.POST._mutable = _mutable

    response = BusinessLineInterestView.as_view()(business_line_interest_view_post_request)

    user_application = business_line_interest_view_post_request.user.application
    assert response.get('Location') == reverse(template)
    assert response.status_code == HTTP_302_FOUND
    assert user_application.interest_in_business == interest_in_business
    assert user_application.business_line == business_line


@mock.patch('openedx.adg.lms.applications.views.render')
@pytest.mark.parametrize(
    'interest_in_business, business_line', [(True, False), (False, True), (False, False)],
    ids=['without_business_line', 'without_interest', 'without_business_line_and_interest']
)
@pytest.mark.django_db
# pylint: disable=unused-argument,protected-access
def test_post_submit_without_required_data_business_line_interest_view(
    mock_render,
    interest_in_business,
    business_line,
    business_line_interest_view_post_request,
    prereqs_completed_business_line_interest_view
):
    """
    Tests that when the user makes a post request in the business line page without adding
    the required data i.e interest_in_business and business line, the user is not taken to a new page
    """
    test_business_line = BusinessLineFactory().id if business_line else None
    test_interest = TEST_INTEREST_IN_BUSINESS if interest_in_business else ''

    _mutable = business_line_interest_view_post_request.POST._mutable
    business_line_interest_view_post_request.POST._mutable = True
    business_line_interest_view_post_request.POST['business_line'] = test_business_line
    business_line_interest_view_post_request.POST['interest_in_business'] = test_interest
    business_line_interest_view_post_request.POST['submit_or_back_clicked'] = 'submit'
    business_line_interest_view_post_request.POST._mutable = _mutable

    BusinessLineInterestView.as_view()(business_line_interest_view_post_request)

    mock_render.assert_called_once_with(
        business_line_interest_view_post_request, 'adg/lms/applications/business_line_interest.html', mock.ANY
    )

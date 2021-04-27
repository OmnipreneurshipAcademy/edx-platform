"""
Helpers for webinars app
"""
from datetime import timedelta
from itertools import chain

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.timezone import now

from openedx.adg.common.lib.mandrill_client.client import MandrillClient
from openedx.adg.common.lib.mandrill_client.tasks import task_cancel_mandrill_emails, task_send_mandrill_email

from .constants import ONE_WEEK_REMINDER_ID_FIELD_NAME, STARTING_SOON_REMINDER_ID_FIELD_NAME


def send_webinar_emails(template_slug, webinar, recipient_emails, send_at=None):
    """
    Send webinar email to the list of given email addresses using the given template and data

    Arguments:
        template_slug (str): Slug for the chosen email template
        webinar (Webinar): Webinar object
        recipient_emails (list):  List of email addresses (str) to send the email to
        send_at (str): A String containing the time at which email will be sent

    Returns:
        None
    """
    context = {
        'webinar_id': webinar.id,
        'webinar_title': webinar.title,
        'webinar_description': webinar.description,
        'webinar_start_time': webinar.start_time.strftime("%B %d, %Y %I:%M %p %Z")
    }

    task_send_mandrill_email.delay(template_slug, recipient_emails, context, send_at)


def send_cancellation_emails_for_given_webinars(cancelled_webinars):
    """
    Sends emails for all the registered users, co-hosts, panelists and the presenter for the given cancelled webinars

    Arguments:
        cancelled_webinars (iterable): Webinars for which to send the cancellation emails

    Returns:
        None
    """
    for cancelled_webinar in cancelled_webinars:
        registered_user_emails = cancelled_webinar.registrations.filter(
            is_registered=True).values_list('user__email', flat=True)
        co_hosts = cancelled_webinar.co_hosts.all().values_list('email', flat=True)
        panelists = cancelled_webinar.panelists.all().values_list('email', flat=True)
        presenter_email_address = cancelled_webinar.presenter.email

        webinar_email_addresses = set(chain(co_hosts, panelists, registered_user_emails, {presenter_email_address}))

        if not webinar_email_addresses:
            continue

        send_webinar_emails(
            MandrillClient.WEBINAR_CANCELLATION,
            cancelled_webinar,
            list(webinar_email_addresses)
        )


def cancel_reminders_for_given_webinars(webinars):
    """
    Cancels all the reminders for the given webinars.

    Args:
        webinars (list): List of webinars for which reminders will be cancelled.

    Returns:
        None
    """
    for webinar in webinars:
        cancel_all_reminders(
            webinar.registrations.webinar_team_and_active_user_registrations()
        )


def send_webinar_registration_email(webinar, email):
    """
    Send webinar registration email to user.

    Args:
        webinar (Webinar): The webinar in which user is registered
        email (str): User's email

    Returns:
        None
    """
    task_send_mandrill_email.delay(MandrillClient.WEBINAR_REGISTRATION_CONFIRMATION, [email], {
        'webinar_title': webinar.title,
        'webinar_description': webinar.description,
        'webinar_link': webinar.meeting_link,
        'webinar_start_time': webinar.start_time.strftime('%b %d, %Y %I:%M %p GMT'),
    })


def schedule_webinar_reminders(user_emails, webinar):
    """
    Schedule reminders for a webinar on mandrill.

    Args:
        user_emails (list): List of user emails to schedule reminders.
        webinar (Webinar): The webinar for which reminders will be scheduled.

    Returns:
        None
    """
    send_webinar_emails(
        MandrillClient.WEBINAR_TWO_HOURS_REMINDER,
        webinar,
        user_emails,
        webinar.start_time - timedelta(hours=2),
    )

    week_before_webinar_start_time = webinar.start_time - timedelta(days=7)

    if week_before_webinar_start_time > now():
        send_webinar_emails(
            MandrillClient.WEBINAR_ONE_WEEK_REMINDER,
            webinar,
            user_emails,
            week_before_webinar_start_time,
        )


def save_scheduled_reminder_ids(mandrill_response, template_name, webinar_id):
    """
    Saves mandrill msg ids of the reminders for a webinar registration.

    Args:
        webinar_id (int): Webinar Id
        mandrill_response (list): List containing the response from mandrill
        template_name (str): Mandrill email template slug

    Returns:
        None
    """
    from openedx.adg.lms.webinars.models import WebinarRegistration

    template_name_to_field_map = {
        MandrillClient.WEBINAR_TWO_HOURS_REMINDER: STARTING_SOON_REMINDER_ID_FIELD_NAME,
        MandrillClient.WEBINAR_ONE_WEEK_REMINDER: ONE_WEEK_REMINDER_ID_FIELD_NAME,
    }

    for response in mandrill_response:
        registration = WebinarRegistration.objects.filter(
            user__email=response['email'], webinar__id=webinar_id
        ).first()
        setattr(registration, template_name_to_field_map[template_name], response['_id'])
        registration.save()


def validate_email_list(emails):
    """
    Validate list of comma separated email addresses

    Arguments:
         emails (str): string of comma separated emails

    Returns:
        error (boolean): True if error is found, False otherwise
        emails (list): list of parsed emails
    """

    emails = [email.strip() for email in emails.split(',') if email.strip()]

    for email in emails:
        try:
            validate_email(email)
        except ValidationError:
            return True, emails

    return False, emails


def webinar_emails_for_panelists_co_hosts_and_presenter(webinar):
    """
    Given a webinar, generate a list of emails for co-hosts, panelists, and presenter

    Arguments:
         webinar (obj): webinar object

    Returns:
        emails (list): list of all emails
    """

    panelist_emails = list(webinar.panelists.exclude(email='').values_list('email', flat=True))
    co_host_emails = list(webinar.co_hosts.exclude(email='').values_list('email', flat=True))
    emails = panelist_emails + co_host_emails
    if webinar.presenter:
        emails.append(webinar.presenter.email)
    return emails


def remove_emails_duplicate_in_other_list(email_list, reference_email_list):
    """
    Remove emails from email_list that are already present in reference_email_list

    Arguments:
        email_list (list): list of emails to verify for duplication
        reference_email_list (list):  list of emails to use as a reference point

    Returns:
        emails (list): list of remaining emails
    """
    return [email for email in email_list if email not in reference_email_list]


def update_webinar_team_registrations(webinar_form):
    """
    Updates webinar team registrations if webinar presenter, cohosts or panelists are updated.

    Args:
        webinar_form (Form): Model form with updated data.

    Returns:
        None
    """
    from openedx.adg.lms.webinars.models import WebinarRegistration

    webinar = webinar_form.instance
    cleaned_data = webinar_form.cleaned_data
    old_team = webinar.webinar_team()
    new_team = set(chain(cleaned_data['co_hosts'], cleaned_data['panelists'], {cleaned_data['presenter']}))

    newly_added_members = list(new_team - old_team)
    removed_members = list(old_team - new_team)

    if newly_added_members:
        WebinarRegistration.create_team_registrations(newly_added_members, webinar)
        schedule_webinar_reminders([user.email for user in newly_added_members], webinar)

    if removed_members:
        WebinarRegistration.remove_team_registrations(removed_members, webinar)

        registrations = WebinarRegistration.objects.filter(
            webinar=webinar, user__in=removed_members, is_registered=False
        )
        cancel_all_reminders(registrations)


def cancel_all_reminders(registrations):
    """
    Cancels reminders by extracting msg ids from the given registrations.

    Args:
        registrations (list): List of registrations for which reminders will be cancelled.

    Returns:
        None
    """
    from openedx.adg.lms.webinars.models import WebinarRegistration

    msg_id_map = {
        'starting_soon_msg_ids': [],
        'one_week_before_msg_ids': [],
    }

    for registration in registrations:
        if registration.starting_soon_mandrill_reminder_id:
            msg_id_map['starting_soon_msg_ids'].append(registration.starting_soon_mandrill_reminder_id)
            registration.starting_soon_mandrill_reminder_id = ''

        if registration.week_before_mandrill_reminder_id:
            msg_id_map['one_week_before_msg_ids'].append(registration.week_before_mandrill_reminder_id)
            registration.week_before_mandrill_reminder_id = ''

    if msg_id_map['starting_soon_msg_ids']:
        task_cancel_mandrill_emails.delay(msg_id_map['starting_soon_msg_ids'])

    if msg_id_map['one_week_before_msg_ids']:
        task_cancel_mandrill_emails.delay(msg_id_map['one_week_before_msg_ids'])

    WebinarRegistration.objects.bulk_update(
        registrations, ['starting_soon_mandrill_reminder_id', 'week_before_mandrill_reminder_id'], batch_size=999
    )

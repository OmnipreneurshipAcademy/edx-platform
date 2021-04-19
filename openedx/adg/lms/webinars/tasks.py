"""
Tasks for webinars
"""
from datetime import datetime, timedelta

from celery.task import task

from openedx.adg.lms.webinars.helpers import cancel_webinar_reminders, reschedule_webinar_reminders
from openedx.adg.lms.webinars.models import WebinarRegistration


@task()
def task_reschedule_webinar_reminders(webinar_id, new_start_time):
    """
    Reschedules all the webinar reminders.

    Args:
        webinar_id (int): Webinar Id for which reminders will be rescheduled.
        new_start_time (str): String containing time in format ("%m/%d/%Y, %H:%M:%S")
    """
    new_start_time = datetime.strptime(new_start_time, '%m/%d/%Y, %H:%M:%S')

    week_before_start_time = new_start_time - timedelta(days=7)
    two_hours_before_start_time = new_start_time - timedelta(hours=2)

    registrations = WebinarRegistration.objects.filter(webinar__id=webinar_id)

    reschedule_webinar_reminders(registrations, str(two_hours_before_start_time), 'starting_soon_mandrill_reminder_id')

    if week_before_start_time > datetime.now():
        reschedule_webinar_reminders(registrations, str(week_before_start_time), 'week_before_mandrill_reminder_id')
    else:
        cancel_webinar_reminders(registrations, 'week_before_mandrill_reminder_id')

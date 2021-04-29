"""
'Webinars' is a Django app built as part of the ADG LMS and Admin experience.

Admin Experience
----------------

This feature enables ADG admins to:
 - create new events(the words 'event' and 'webinar' are used interchangeably) on the admin site
 - update existing events
 - cancel existing events
 - clone existing events
 - view all events i.e. upcoming, cancelled and delivered
 - view list of registered users against events

While creating a new event, admins can:
 - add event details like title, schedule, description, banner image, external meeting link for webinar
 - add presenters, co-hosts and panelists
 - choose event language out of English and Arabic
 - send email invites to all Omni Academy users
 - send email invites to outsiders by providing their email addresses

While updating an existing event, admins can:
 - update event details, language, presenters, co-hosts and panelists
 - send new invites
 - send update email to all registered users

Learner Experience
------------------

It also enables ADG learners to:
 - view a list of upcoming events on the LMS site
 - view details of an event
 - register for an upcoming event and attend a webinar via an external link
 - cancel registration

When an event is cancelled by an admin, all users registered in the event receive a cancellation email.

All registered users of an event also receive automated reminder emails.
"""

default_app_config = 'openedx.adg.lms.webinars.apps.WebinarsConfig'

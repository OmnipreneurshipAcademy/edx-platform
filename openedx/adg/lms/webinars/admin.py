"""
Registering models for webinars app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from openedx.adg.common.lib.mandrill_client.client import MandrillClient
from openedx.adg.lms.applications.admin import adg_admin_site

from .constants import SEND_UPDATE_EMAILS_FIELD
from .forms import WebinarForm
from .helpers import (
    get_newly_added_and_removed_team_members,
    get_webinar_invitees_emails,
    get_webinar_update_recipients_emails,
    remove_emails_duplicate_in_other_list,
    remove_team_registrations_and_cancel_reminders,
    schedule_webinar_reminders,
    send_webinar_emails,
    webinar_emails_for_panelists_co_hosts_and_presenter
)
from .models import CancelledWebinar, Webinar, WebinarRegistration


class ActiveWebinarStatusFilter(admin.SimpleListFilter):
    """
    Custom filter to provide `Upcoming` and `Delivered` states filter functionality to the WebinarAdmin
    """

    title = _('Webinar Status')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            (Webinar.UPCOMING, _('Upcoming')),
            (Webinar.DELIVERED, _('Delivered')),
        )

    def queryset(self, request, queryset):
        if self.value() == Webinar.UPCOMING:
            return queryset.filter(status=Webinar.UPCOMING)

        if self.value() == Webinar.DELIVERED:
            return queryset.filter(status=Webinar.DELIVERED)


class WebinarAdminBase(admin.ModelAdmin):
    """
    Base Model admin for webinars i.e Cancelled Webinars and Non-Cancelled Webinars
    """

    save_as = True
    list_display = ('title', 'start_time', 'presenter', 'status',)
    raw_id_fields = ('presenter', 'co_hosts', 'panelists')
    search_fields = ('title',)
    filter_horizontal = ('co_hosts', 'panelists',)


class WebinarAdmin(WebinarAdminBase):
    """
    Admin for upcoming and delivered webinars
    """

    list_filter = ('start_time', 'language', ActiveWebinarStatusFilter)
    readonly_fields = ('created_by', 'modified_by', 'status',)

    form = WebinarForm

    def get_fields(self, request, obj=None):
        """
        Override `get_fields` to dynamically set fields to be rendered.
        """
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove(SEND_UPDATE_EMAILS_FIELD)
        return fields

    def save_related(self, request, form, formsets, change):
        """
        Extension of save_related for webinar to send emails when object is created or modified.
        """
        new_members = []
        removed_members = []
        if change and any(field in form.changed_data for field in ['co_hosts', 'presenter', 'panelists']):
            new_members, removed_members = get_newly_added_and_removed_team_members(form)

        super().save_related(request, form, formsets, change)

        webinar = form.instance

        webinar_invitees_emails = get_webinar_invitees_emails(form)

        if change:
            if removed_members:
                remove_team_registrations_and_cancel_reminders(removed_members, webinar)

            webinar_update_recipients_emails = []
            if new_members or webinar_invitees_emails or form.cleaned_data.get(SEND_UPDATE_EMAILS_FIELD):
                webinar_update_recipients_emails = get_webinar_update_recipients_emails(webinar)

            if form.cleaned_data.get(SEND_UPDATE_EMAILS_FIELD):
                send_webinar_emails(
                    MandrillClient.WEBINAR_UPDATED,
                    webinar,
                    webinar_update_recipients_emails
                )

            if new_members:
                WebinarRegistration.create_team_registrations(new_members, webinar)

                new_member_emails = [user.email for user in new_members]
                schedule_webinar_reminders(new_member_emails, webinar.to_dict())

                webinar_invitees_emails += new_member_emails

            webinar_invitees_emails = remove_emails_duplicate_in_other_list(
                webinar_invitees_emails, webinar_update_recipients_emails
            )

        else:
            webinar_team_emails = webinar_emails_for_panelists_co_hosts_and_presenter(webinar)
            webinar_invitees_emails += webinar_team_emails

            WebinarRegistration.create_team_registrations(User.objects.filter(email__in=webinar_team_emails), webinar)
            schedule_webinar_reminders(webinar_team_emails, webinar.to_dict())

        if webinar_invitees_emails:
            send_webinar_emails(
                MandrillClient.WEBINAR_CREATED,
                webinar,
                list(set(webinar_invitees_emails)),
            )

    def get_queryset(self, request):
        qs = super(WebinarAdmin, self).get_queryset(request)
        return qs.filter(~Q(status=Webinar.CANCELLED))


class CancelledWebinarAdmin(WebinarAdminBase):
    """
    Model admin for cancelled webinar
    """

    save_as = False

    def get_queryset(self, request):
        qs = super(CancelledWebinarAdmin, self).get_queryset(request)
        return qs.filter(status=Webinar.CANCELLED)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class WebinarRegistrationAdmin(admin.ModelAdmin):
    """
    Model admin for webinar registration
    """

    list_display = ('webinar', 'user', 'is_registered', 'is_team_member_registration',)
    search_fields = ('webinar__title', 'user__username')
    list_filter = ('webinar',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReadOnlyUserAdmin(UserAdmin):
    """
    Readonly User admin to allow search when adding users in fields in ADG Admin site
    """

    def has_add_permission(self, request):
        """
        Do not allow admin to add a new User object
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Do not allow admin to change any User object
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Do not allow admin to delete an existing User object
        """
        return False

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the User model from admin site index
        """
        return {}


admin.site.register(Webinar, WebinarAdmin)
adg_admin_site.register(Webinar, WebinarAdmin)

admin.site.register(CancelledWebinar, CancelledWebinarAdmin)
adg_admin_site.register(CancelledWebinar, CancelledWebinarAdmin)

admin.site.register(WebinarRegistration, WebinarRegistrationAdmin)
adg_admin_site.register(WebinarRegistration, WebinarRegistrationAdmin)

adg_admin_site.register(User, ReadOnlyUserAdmin)

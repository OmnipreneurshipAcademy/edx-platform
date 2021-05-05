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

from .forms import WebinarForm
from .helpers import (
    remove_emails_duplicate_in_other_list,
    schedule_webinar_reminders,
    send_webinar_emails,
    update_webinar_team_registrations,
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
    raw_id_fields = ('presenter', 'co_hosts', 'panelists')
    readonly_fields = ('created_by', 'modified_by', 'status',)

    form = WebinarForm

    def get_fields(self, request, obj=None):
        """
        Override `get_fields` to dynamically set fields to be rendered.
        """
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove('send_update_emails_to_registrants')
        return fields

    def save_related(self, request, form, formsets, change):
        """
        Extension of save_related for webinar to send emails when object is created or modified.
        """
        if change and any(field in form.changed_data for field in ['co_hosts', 'presenter', 'panelists']):
            update_webinar_team_registrations(form)

        super(WebinarAdmin, self).save_related(request, form, formsets, change)

        webinar = form.instance

        webinar_invitation_recipients = form.cleaned_data.get('invites_by_email_address', [])
        if form.cleaned_data.get('invite_all_platform_users'):
            webinar_invitation_recipients += list(
                User.objects.exclude(email='').values_list('email', flat=True)
            )

        if change:
            registered_users = list(
                webinar.registrations.filter(is_registered=True).values_list('user__email', flat=True)
            )
            if form.cleaned_data.get('send_update_emails_to_registrants'):
                send_webinar_emails(
                    MandrillClient.WEBINAR_UPDATED,
                    webinar,
                    list(set(registered_users))
                )

            webinar_invitation_recipients = remove_emails_duplicate_in_other_list(
                webinar_invitation_recipients, registered_users
            )
        else:
            webinar_team_emails = webinar_emails_for_panelists_co_hosts_and_presenter(webinar)
            webinar_invitation_recipients += webinar_team_emails

            WebinarRegistration.create_team_registrations(User.objects.filter(email__in=webinar_team_emails), webinar)
            schedule_webinar_reminders(list(set(webinar_team_emails)), webinar.to_dict())

        send_webinar_emails(
            MandrillClient.WEBINAR_CREATED,
            webinar,
            list(set(webinar_invitation_recipients)),
        )

    def get_queryset(self, request):
        qs = super(WebinarAdmin, self).get_queryset(request)
        return qs.filter(~Q(status=Webinar.CANCELLED))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if '_saveasnew' in request.POST:
            request.POST = request.POST.copy()
            request.POST['status'] = Webinar.UPCOMING
        return self.changeform_view(request, object_id, form_url, extra_context)


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

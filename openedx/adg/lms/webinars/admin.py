"""
Registering models for webinars app.
"""
from django.contrib import admin

from openedx.adg.lms.applications.admin import adg_admin_site

from .models import Webinar, WebinarRegistration


@admin.register(Webinar)
class WebinarAdmin(admin.ModelAdmin):
    """
    Model admin for webinar
    """

    save_as = True

    list_display = ('title', 'start_time', 'presenter', 'status',)
    list_filter = ('start_time', 'status', 'language',)
    search_fields = ('title',)
    raw_id_fields = ('presenter', 'co_hosts', 'panelists')
    readonly_fields = ('created_by', 'modified_by',)
    filter_horizontal = ('co_hosts', 'panelists',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.modified_by = request.user
        obj.save()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if '_saveasnew' in request.POST:
            request.POST = request.POST.copy()
            request.POST['status'] = Webinar.UPCOMING
        return self.changeform_view(request, object_id, form_url, extra_context)


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(admin.ModelAdmin):
    """
    Model admin for webinar registration
    """

    list_display = ('webinar', 'user', 'is_registered',)
    search_fields = ('webinar',)


adg_admin_site.register(Webinar, WebinarAdmin)
adg_admin_site.register(WebinarRegistration, WebinarRegistrationAdmin)

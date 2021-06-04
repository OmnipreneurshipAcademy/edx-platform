"""
All views for applications app
"""
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from rest_framework.status import HTTP_400_BAD_REQUEST

from openedx.adg.lms.applications.forms import (
    ExtendedUserProfileForm,
    UserApplicationCoverLetterForm,
    UserApplicationForm,
    UserProfileForm
)
from openedx.adg.lms.registration_extension.models import ExtendedUserProfile
from openedx.adg.lms.utils.date_utils import month_choices, year_choices

from .helpers import send_application_submission_confirmation_email
from .models import ApplicationHub, BusinessLine, Education, MultilingualCourseGroup, UserApplication


class RedirectToLoginOrRelevantPageMixin(AccessMixin):
    """
    AccessView that allows only authenticated users with pre_conditions satisfied to access the view.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects to login page for unauthenticated users. Runs `handle_no_permission` if preconditions are not
        satisfied. Runs the view normally for authenticated user with proper conditions satisfied.
        """
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        elif not self.is_precondition_satisfied():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def is_precondition_satisfied(self):
        """
        Checks if a written application is already submitted or not.

        Returns:
            bool: True if written application is not completed, False otherwise.
        """
        user_application_hub, _ = ApplicationHub.objects.get_or_create(user=self.request.user)

        return not user_application_hub.is_written_application_completed

    def handle_no_permission(self):
        """
        Redirects to application hub on get request or returns http 400 on post request.

        Returns:
            HttpResponse object.
        """
        if self.request.method == 'POST':
            return HttpResponse(status=HTTP_400_BAD_REQUEST)
        else:
            return redirect('application_hub')


class ApplicationHubView(RedirectToLoginOrRelevantPageMixin, View):
    """
    View to display application hub, a checklist entailing different parts of the application process, and allow
    users to submit their application.
    """

    template_name = 'adg/lms/applications/hub.html'

    def is_precondition_satisfied(self):
        """
        Checks if a user's application is already submitted or not.

        Returns:
            Boolean, True or False.
        """
        user_application_hub, _ = ApplicationHub.objects.get_or_create(user=self.request.user)

        if self.request.method == 'POST':
            return user_application_hub.are_application_pre_reqs_completed()
        else:
            return not user_application_hub.is_application_submitted

    def handle_no_permission(self):
        """
        Redirects on test failure, `is_precondition_satisfied()` returns False.

        Returns:
            HttpResponse object.
        """
        if self.request.method == 'POST':
            return HttpResponse(status=400)
        else:
            return redirect('application_success')

    def get(self, request):
        """
        Send the context data i.e user_application_hub, pre_req courses, and percentage to the template for rendering.

        Returns:
            HttpResponse object.
        """
        user_application_hub, _ = ApplicationHub.objects.get_or_create(user=self.request.user)
        pre_req_courses = MultilingualCourseGroup.objects.get_user_program_prereq_courses(request.user)

        return render(
            request,
            self.template_name,
            context={'user_application_hub': user_application_hub, 'pre_req_courses': pre_req_courses}
        )

    def post(self, request):
        """
        Submit user application, send mandrill email according to the Application Confirmation Email format. In the
        end, it redirects to the application success page.

        Returns:
            HttpResponse object.
        """
        if not request.user.application_hub.is_application_submitted:
            request.user.application_hub.submit_application_for_current_date()
            send_application_submission_confirmation_email(request.user.email)
        return redirect('application_success')


class ApplicationSuccessView(RedirectToLoginOrRelevantPageMixin, TemplateView):
    """
    View entailing successfully submitted application status of a user.
    """

    template_name = 'adg/lms/applications/success.html'

    def is_precondition_satisfied(self):
        """
        Checks if a user's application is already submitted or not.

        Returns:
            Boolean, True or False.
        """
        try:
            return self.request.user.application_hub.is_application_submitted
        except ApplicationHub.DoesNotExist:
            return False

    def handle_no_permission(self):
        """
        Redirects on test failure, `test_func()` returns False.

        Returns:
            HttpResponse object.
        """
        return HttpResponse(status=400)

    def get_context_data(self, **kwargs):
        """
        Send the application submission date for the authenticated user in the context dictionary.

        Returns:
            dict object.
        """
        context = super(ApplicationSuccessView, self).get_context_data(**kwargs)
        context['submission_date'] = self.request.user.application_hub.submission_date
        return context


class ContactInformationView(RedirectToLoginOrRelevantPageMixin, View):
    """
    View for the contact information of user application
    """

    login_url = reverse_lazy('register_user')
    template_name = 'adg/lms/applications/contact_info.html'
    user_profile_form = None
    extended_profile_form = None
    application_form = None

    def is_precondition_satisfied(self):
        """
        Checks if a written application is already submitted or not.

        Returns:
            bool: True if written application is not completed, False otherwise.
        """
        user_application_hub, _ = ApplicationHub.objects.get_or_create(user=self.request.user)

        return not user_application_hub.is_written_application_completed

    def handle_no_permission(self):
        """
        Redirects to application hub on get request or returns http 400 on post request.

        Returns:
            HttpResponse object.
        """
        if self.request.method == 'POST':
            return HttpResponse(status=HTTP_400_BAD_REQUEST)
        else:
            return redirect('application_hub')

    def get(self, request):
        """
        Send the context data to the template for rendering.

        Returns:
            HttpResponse object.
        """
        return render(request, self.template_name, self.initialize_forms(request))

    def post(self, request):
        """
        Submit user contact information data. If successful, redirects to the experience page.
        If resume is added, then experience page is skipped and redirect to application cover letter page.

        Returns:
            HttpResponse object.
        """
        forms = self.initialize_forms(request)
        if self.is_valid():

            self.user_profile_form.save()
            self.extended_profile_form.save(request=request)
            instance = self.application_form.save(commit=False)
            instance.user = request.user
            if self.application_form.data.get('delete-file') == 'Yes':
                instance.resume.delete()
            instance.save()

            if self.application_form.cleaned_data.get('resume'):
                return redirect(reverse_lazy('application_cover_letter'))
            return redirect(reverse_lazy('application_education_experience'))
        return render(request, self.template_name, forms)

    def is_valid(self):
        """
        Send the context data to the template for rendering.

        Returns:
            Boolean object.
        """
        return (self.user_profile_form.is_valid() and self.extended_profile_form.is_valid()
                and self.application_form.is_valid())

    def initialize_forms(self, request):
        """
        Initialize the form with available data

        Returns:
            None.
        """
        application = UserApplication.objects.filter(user=request.user).first()

        if request.method == 'GET':
            self.user_profile_form = UserProfileForm(instance=request.user.profile)
            self.extended_profile_form = ExtendedUserProfileForm(initial=self.get_context_data(request))
            self.application_form = UserApplicationForm(instance=application)

        elif request.method == 'POST':
            self.user_profile_form = UserProfileForm(request.POST, instance=request.user.profile)
            self.extended_profile_form = ExtendedUserProfileForm(request.POST)
            self.application_form = UserApplicationForm(request.POST, request.FILES, instance=application)

        return {
            'user_profile_form': self.user_profile_form,
            'extended_profile_form': self.extended_profile_form,
            'application_form': self.application_form,
        }

    def get_context_data(self, request):
        """
        Initialize the data for extended profile form

        Returns:
            Dict.
        """
        context = {'email': request.user.email}
        extended_profile = ExtendedUserProfile.objects.filter(user=request.user).first()
        if extended_profile:
            context['saudi_national'] = extended_profile.saudi_national
            context['organization'] = extended_profile.company

            if extended_profile.birth_date:
                context.update({
                    'birth_day': extended_profile.birth_date.day,
                    'birth_month': extended_profile.birth_date.month,
                    'birth_year': extended_profile.birth_date.year,
                })
        return context


class EducationAndExperienceView(RedirectToLoginOrRelevantPageMixin, TemplateView):
    """
    Education and Experience View
    """

    login_url = reverse_lazy('register_user')
    template_name = 'adg/lms/applications/education_experience.html'

    def get_context_data(self, **kwargs):
        """
        Context data to pre-fill forms and dropdown options.

        Returns:
            Dict.
        """
        context = super().get_context_data(**kwargs)
        user_application = self.request.user.application
        context.update({
            'degree_types': Education.DEGREE_TYPES,
            'month_choices': month_choices(),
            'year_choices': year_choices(),
            'user_application_id': user_application.id,
            'is_work_experience_not_applicable': user_application.is_work_experience_not_applicable,
            'is_education_experience_completed': user_application.is_education_experience_completed,
        })

        return context

    def is_precondition_satisfied(self):
        """
        Checks if a user's application is started but not completed.

        Returns:
            Boolean, True or False.
        """
        application_hub = getattr(self.request.user, 'application_hub', None)

        return (
            application_hub and
            application_hub.is_written_application_started and
            not application_hub.is_written_application_completed
        )

    def handle_no_permission(self):
        """
        Redirects to application hub.
        """
        return redirect('application_hub')


class CoverLetterView(RedirectToLoginOrRelevantPageMixin, View):
    """
    View enabling the user to select a Business Line and upload or write a cover letter.
    """

    template_name = 'adg/lms/applications/cover_letter.html'
    login_url = reverse_lazy('register_user')

    def get(self, request):
        """
        Send the context data for example a list of business lines and saved user_application.

        Returns:
            HttpResponse object.
        """
        try:
            form = UserApplicationCoverLetterForm(instance=request.user.application)
        except UserApplication.DoesNotExist:
            form = None

        return self.handle_rendering(request, form)

    def post(self, request):
        """
        Submit user application and redirect to application hub, experience or contact depending upon button click and
        existence of resume.

        Returns:
            HttpResponse object.
        """
        user_application, _ = UserApplication.objects.get_or_create(user=request.user)
        form = UserApplicationCoverLetterForm(request.POST, request.FILES, instance=user_application)

        if form.is_valid():
            form.save_form(request.POST)
        else:
            return self.handle_rendering(request, form)

        return self.handle_redirection(request, form, user_application)

    def handle_rendering(self, request, form):
        """
        Create context and render cover letter template

        Returns:
            HttpResponse object.
        """
        context = {
            'business_lines': BusinessLine.objects.all(),
            'application_form': form,
        }

        return render(request, self.template_name, context)

    def handle_redirection(self, request, form, application):
        """
        Redirects to contact template if resume exists otherwise to experience on clicking back button and to
        application hub on clicking submit

        Returns:
            HttpResponse object.
        """
        if form.data.get('button_click') == 'back':
            if application.resume:
                return redirect('application_contact')

            return redirect('application_education_experience')
        else:
            application_hub = request.user.application_hub
            application_hub.submit_written_application_for_current_date()

            return redirect('application_hub')


class ApplicationIntroductionView(RedirectToLoginOrRelevantPageMixin, TemplateView):
    """
    View for Application introduction page
    """

    login_url = reverse_lazy('register_user')
    template_name = 'adg/lms/applications/introduction.html'

    def is_precondition_satisfied(self):
        """
        Checks if a user has visited the application hub page i.e ApplicationHub object for current user exists or not

        Returns:
            bool: True if user has visited the hub page else False
        """
        return not ApplicationHub.objects.filter(user=self.request.user).exists()

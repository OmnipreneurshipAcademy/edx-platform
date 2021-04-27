"""
API views for webinar app
"""
from django.http import HttpResponseServerError
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from openedx.core.lib.api.view_utils import view_auth_classes

from .helpers import send_webinar_registration_email
from .models import Webinar, WebinarRegistration


@view_auth_classes(is_authenticated=True)
class WebinarRegistrationView(APIView):
    """
    A view to register user in a webinar event or cancel already registered user in a webinar.
    """

    @method_decorator(ensure_csrf_cookie)
    def post(self, request, pk, action):
        """
        Register in a webinar or cancel registration

        Args:
            request (HttpRequest): HTTP request
            pk (int): Webinar id, the primary key of model
            action (str): Actions to perform on event i.e. `register` or `cancel`

        Returns:
            HttpResponse: On success returns response with status code 200 otherwise
            throw HTTP error code as per nature of error i.e. 404 or 500
        """
        webinar = Webinar.objects.filter(pk=pk).first()
        if not webinar:
            return HttpResponseServerError(_('Webinar not found'))

        if webinar.status == Webinar.CANCELLED:
            return HttpResponseServerError(_('Webinar has been cancelled'))

        is_registering = action == 'register'
        user = request.user

        registered_webinar_for_user = WebinarRegistration.objects.filter(
            webinar=webinar, user=user, is_registered=is_registering
        ).first()

        if not registered_webinar_for_user:
            WebinarRegistration.objects.update_or_create(
                webinar=webinar, user=user, defaults={'is_registered': is_registering}
            )
            # pylint: disable=expression-not-assigned
            send_webinar_registration_email(webinar, user.email) if is_registering else None

        return Response({}, status=HTTP_200_OK)

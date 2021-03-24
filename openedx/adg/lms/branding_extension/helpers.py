"""
Helpers for branding_extension app
"""
from datetime import datetime
from urllib import parse

from django.conf import settings
from django.utils.translation import ugettext as _

from common.djangoapps.edxmako.shortcuts import marketing_link
from lms.djangoapps.branding.api import _build_support_form_url
from openedx.adg.lms.utils.env_utils import is_testing_environment
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


def get_footer_navigation_links():
    """
    Helper to get navigation links for the footer

    Returns:
        List, which contains dictionaries of url
    """
    links = [
        (marketing_link('ABOUT'), _('About')),
        (marketing_link('OUR_TEAM'), _('Our Team')),
        (marketing_link('TOS'), _('Terms')),
        (_build_support_form_url(), _('Contact')),
    ]

    return [
        {
            'url': link_url,
            'title': link_title,
        }
        for link_url, link_title in links
    ]


def get_copyright():
    """
    Helper to get copyright for ADG

    Returns:
       str, A string which contains a copyright text
    """
    return u'\u00A9 {year} {org_name}'.format(
        year=datetime.today().year,
        org_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME)
    )


def is_referred_by_login_or_register(request):
    """
    Returns True if user is redirected from login or register, otherwise False

    Arguments:
        request: HTTP request

    Returns:
        Boolean: True if path in HTTP_REFERER contains login or register, otherwise False
    """
    if is_testing_environment():
        return True

    referer = request.META.get('HTTP_REFERER', '')
    path = parse.urlsplit(referer).path
    return path in ['/login', '/register']

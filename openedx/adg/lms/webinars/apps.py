"""
All configurations for webinars app
"""
from django.apps import AppConfig


class WebinarsConfig(AppConfig):
    """
    Webinars app configuration.
    """

    name = 'openedx.adg.lms.webinars'

    def ready(self):
        from . import handlers  # pylint: disable=unused-import

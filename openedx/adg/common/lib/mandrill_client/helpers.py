"""
Helper methods for mandrill_client
"""
from django.conf import settings
from django.utils.translation import get_language


def add_user_preferred_language_to_template_slug(template):
    """
    Modify template slug according to user preferred language

    Arguments:
        template (string): template slug

    Returns:
        string: template slug
    """

    user_lang = get_language()
    if user_lang != settings.LANGUAGE_CODE:
        return '{}-{}'.format(template, user_lang)
    return template

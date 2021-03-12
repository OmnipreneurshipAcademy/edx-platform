"""
All tests for mandrill_client helper methods
"""
import pytest
from django.utils import translation

from openedx.adg.common.lib.mandrill_client.helpers import add_user_preferred_language_to_template_slug


@pytest.mark.parametrize('slug, language, expected', [
    ('template-name', 'en', 'template-name'),
    ('template-name', 'ar', 'template-name-ar')
])
def test_add_user_preferred_language_to_template_slug(slug, language, expected):
    """
    Assert that Mandrill function returns template slug as per user selected language
    """
    translation.activate(language)
    assert add_user_preferred_language_to_template_slug(slug) == expected

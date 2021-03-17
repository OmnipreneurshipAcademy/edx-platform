"""
All tests for mandrill_client helper methods
"""
import pytest

from common.djangoapps.student.tests.factories import UserFactory
from openedx.adg.common.lib.mandrill_client.helpers import add_user_preferred_language_to_template_slug
from openedx.core.djangoapps.user_api.tests.factories import UserPreferenceFactory


@pytest.fixture(name='user')
def user_fixture():
    """
    Create user and related profile factories
    """
    return UserFactory()


@pytest.mark.parametrize('slug, language, expected', [
    ('template-name', 'en', 'template-name'),
    ('template-name', 'ar', 'template-name-ar')
])
@pytest.mark.django_db
def test_add_user_preferred_language_to_template_slug(user, slug, language, expected):
    """
    Assert that Mandrill function returns template slug as per user selected language
    """
    UserPreferenceFactory.build(
        user=user,
        key='pref-lang',
        value=language,
    ).save()
    assert add_user_preferred_language_to_template_slug(slug, user.email) == expected

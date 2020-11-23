"""
Tests for models.
"""
from django.test import TestCase
from openedx.adg.lms.bootcamps.models import Bootcamp


class ModelTestCase(TestCase):
    """
    TestCase for models
    """

    def setUp(self):
        super(ModelTestCase, self).setUp()
        self.bootcamp = Bootcamp.objects.create(title='test-bootcamp')

    def test_str(self):
        """
        Tests if the __str__ method returns the title as expected or not
        """
        self.assertEqual(self.bootcamp.title, self.bootcamp.__str__())

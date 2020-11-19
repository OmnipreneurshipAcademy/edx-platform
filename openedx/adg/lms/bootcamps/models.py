"""
Models for Bootcamps application.
"""
from django.db import models
from model_utils.models import TimeStampedModel

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class Bootcamp(TimeStampedModel):
    """
    Model for all required parts of a bootcamp.
    """
    title = models.CharField(max_length=100)
    courses = models.ManyToManyField(
        CourseOverview,
        related_name='bootcamps',
    )

    class Meta:
        ordering = ['created']
        app_label = 'bootcamps'

    def __str__(self):
        return self.title

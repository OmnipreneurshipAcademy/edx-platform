"""
All models for applications app
"""
from django.db import models
from model_utils.models import TimeStampedModel

from django.contrib.auth.models import User
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class MiniDegree(TimeStampedModel):
    """
    Model for storing basic information about a mini degree
    """
    user = models.ForeignKey(User, related_name='mini_degree', on_delete=models.CASCADE, )
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    courses = models.ManyToManyField(CourseOverview, related_name='mini_degree_courses')

    class Meta:
        app_label = 'mini_degree'

    def __str__(self):
        return 'MiniDegree {}'.format(self.title)

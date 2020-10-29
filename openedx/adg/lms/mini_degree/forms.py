"""Forms for Mini Degree"""

from django import forms

from .models import MiniDegree
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class MiniDegreeForm(forms.ModelForm):
    class Meta:
        model = MiniDegree
        exclude = ['user']

    courses = forms.ModelMultipleChoiceField(queryset=CourseOverview.objects.all(),
                                             widget=forms.CheckboxSelectMultiple)

    def clean_courses(self):
        value = self.cleaned_data['courses']
        if len(value) > 3:
            raise forms.ValidationError("Maximum 3 courses are allowed.")
        if len(value) < 1:
            raise forms.ValidationError("Minimum 1 course is required.")
        return value

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['courses'] = [t.pk for t in kwargs['instance'].courses.all()]
        forms.ModelForm.__init__(self, *args, **kwargs)

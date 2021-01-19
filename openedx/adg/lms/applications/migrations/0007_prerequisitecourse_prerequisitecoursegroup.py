# Generated by Django 2.2.15 on 2021-01-19 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('course_overviews', '0022_courseoverviewtab_is_hidden'),
        ('applications', '0006_auto_20210107_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrerequisiteCourseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Course group name')),
            ],
        ),
        migrations.CreateModel(
            name='PrerequisiteCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='prereq_courses', to='course_overviews.CourseOverview', verbose_name='Multilingual version of a course')),
                ('prereq_course_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prereq_courses', to='applications.PrerequisiteCourseGroup')),
            ],
            options={
                'unique_together': {('course', 'prereq_course_group')},
            },
        ),
    ]

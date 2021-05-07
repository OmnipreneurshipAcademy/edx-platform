# Generated by Django 2.2.20 on 2021-05-07 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0005_auto_20210503_1311'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webinar',
            name='status',
        ),
        migrations.AddField(
            model_name='webinar',
            name='is_cancelled',
            field=models.BooleanField(default=False, verbose_name='Is Event Cancelled'),
        ),
    ]

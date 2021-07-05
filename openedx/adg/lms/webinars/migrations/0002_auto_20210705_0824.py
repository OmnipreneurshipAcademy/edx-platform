# Generated by Django 2.2.17 on 2021-07-05 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webinar',
            name='invites_by_email_address',
            field=models.TextField(blank=True, help_text='Add comma separated emails e.g. example1@domain.com,example2@domain.com', verbose_name='Add guests by email address'),
        ),
        migrations.AddField(
            model_name='webinar',
            name='is_published',
            field=models.BooleanField(default=False, help_text='If you publish the webinar, email invitations will be sent to all the added recipients and learners will be able to see the webinar and register themselves in it.', verbose_name='Publish Webinar'),
        ),
    ]

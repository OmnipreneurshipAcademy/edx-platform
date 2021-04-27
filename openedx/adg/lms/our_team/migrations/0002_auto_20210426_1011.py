# Generated by Django 2.2.17 on 2021-04-26 10:11

import django.core.validators
from django.db import migrations, models
import openedx.adg.lms.our_team.helpers


class Migration(migrations.Migration):

    dependencies = [
        ('our_team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ourteammember',
            name='member_type',
            field=models.CharField(choices=[('team_member', 'Team Member'), ('board_of_trustee', 'Board Of Trustee')], default='team_member', max_length=20, verbose_name='Member Type'),
        ),
        migrations.AlterField(
            model_name='ourteammember',
            name='description',
            field=models.TextField(help_text='Add a description of max 200 characters', max_length=200, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='ourteammember',
            name='designation',
            field=models.CharField(help_text='Add a designation of max 70 characters', max_length=70, verbose_name='Designation'),
        ),
        migrations.AlterField(
            model_name='ourteammember',
            name='image',
            field=models.ImageField(help_text='Add a square image i.e image with 1:1 aspect ratio for optimal results', upload_to='team-members/images/', validators=[django.core.validators.FileExtensionValidator(('png', 'jpg', 'jpeg', 'svg')), openedx.adg.lms.our_team.helpers.validate_profile_image_size], verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='ourteammember',
            name='name',
            field=models.CharField(help_text='Add a name of max 70 characters', max_length=70, verbose_name='Name'),
        ),
    ]

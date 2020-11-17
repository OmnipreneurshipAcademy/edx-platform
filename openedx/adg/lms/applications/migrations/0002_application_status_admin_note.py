# Generated by Django 2.2.16 on 2020-11-16 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userapplication',
            name='reviewed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userapplication',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('accepted', 'Accepted'), ('waitlist', 'Waitlist')], default='open', max_length=8, verbose_name='Application Status'),
        ),
        migrations.CreateModel(
            name='AdminNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('admin_note', models.TextField(blank=True, verbose_name='Admin Note')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.UserApplication')),
            ],
        ),
    ]

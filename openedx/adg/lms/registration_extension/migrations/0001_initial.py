# Generated by Django 2.2.15 on 2020-11-19 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedUserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(blank=True, choices=[('Tanmiah', 'Tanmiah Food Group'), ('Petromin', 'Petromin'), ('RSI', 'Red Sea International'), ('Dukan', 'Dukan'), ('SAED', 'SAED'), ('BARQ', 'BARQ System'), ('PPC', 'Premium Paints Company'), ('IPD', 'International Project Developers'), ('ADG', 'Al-Dabbagh Group')], max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='extended_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

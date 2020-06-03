# Generated by Django 3.0.1 on 2020-04-26 23:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('venues', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='handshakerequestfromvenue',
            name='_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venues.Venue'),
        ),
        migrations.AddField(
            model_name='handshakerequestfromvenue',
            name='_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

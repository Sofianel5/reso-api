# Generated by Django 3.0.1 on 2020-04-27 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geolocation', '0001_initial'),
        ('users', '0002_peertovenuehandshake_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='geolocation.Address'),
        ),
        migrations.AddField(
            model_name='account',
            name='coordinates',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='geolocation.Coordinates'),
        ),
    ]

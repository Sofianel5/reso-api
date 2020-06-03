# Generated by Django 2.2.9 on 2020-06-02 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0011_timeslot_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='attending',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='external_attendees',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='venue',
            name='capacity',
            field=models.IntegerField(default=10),
            preserve_default=False,
        ),
    ]
# Generated by Django 2.2.9 on 2020-06-18 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0015_schedule_scheduleday'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='visit_length',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]

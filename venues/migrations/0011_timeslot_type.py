# Generated by Django 3.0.1 on 2020-05-01 23:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('venues', '0010_auto_20200430_0401'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='type',
            field=models.CharField(choices=[('All', 'All'), ('Eldery', 'Elderly'), ('Frontline', 'Frontline')],
                                   default='All', max_length=25),
        ),
    ]

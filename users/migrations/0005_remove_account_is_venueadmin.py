# Generated by Django 3.0.1 on 2020-05-17 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20200510_2355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_venueadmin',
        ),
    ]

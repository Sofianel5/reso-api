# Generated by Django 3.0.1 on 2020-04-28 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0005_auto_20200427_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='description',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]

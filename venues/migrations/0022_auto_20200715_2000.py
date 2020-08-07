# Generated by Django 2.2.9 on 2020-07-15 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0021_auto_20200714_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='mask_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='form_url',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]

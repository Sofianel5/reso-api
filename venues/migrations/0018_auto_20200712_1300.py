# Generated by Django 2.2.9 on 2020-07-12 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0017_venue_visible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='venue',
            name='type',
            field=models.CharField(choices=[('Retail', 'Retail'), ('Real Estate', 'Real Estate'), ('Restaurant', 'Restaurant'), ('Grocery', 'Grocery'), ('Coffee', 'Coffee'), ('Gym', 'Gym'), ('Gas', 'Gas'), ('Mail', 'Mail'), ('Laundry', 'Laundry'), ('Repair', 'Repair'), ('Beauty', 'Beauty'), ('Education', 'Education')], max_length=20),
        ),
    ]
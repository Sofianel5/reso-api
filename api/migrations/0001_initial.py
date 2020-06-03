# Generated by Django 3.0.1 on 2020-04-26 23:49

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HandshakeRequestFromVenue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_confirmed', models.BooleanField(default=False)),
                ('to_confirmed', models.BooleanField(default=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('thread_id', models.UUIDField(default=uuid.uuid4, unique=True)),
            ],
        ),
    ]

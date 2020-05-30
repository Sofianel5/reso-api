# Generated by Django 2.2.9 on 2020-05-30 01:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('term_length', models.CharField(choices=[('1w', '1 week'), ('1m', '1 month'), ('3m', '3 months'), ('6m', '6 months'), ('1y', '1 year')], max_length=4)),
                ('next_renewal', models.DateTimeField()),
                ('cost', models.DecimalField(decimal_places=2, max_digits=100)),
                ('coupon_code', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('S', 'Small'), ('M', 'Medium'), ('L', 'Large'), ('XL', 'Extra large'), ('C', 'Custom')], max_length=5)),
                ('daily_allowed_scans', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(max_length=120)),
                ('order_id', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('success', models.BooleanField(default=True)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to='ecommerce.Subscription')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.AddField(
            model_name='subscription',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='ecommerce.SubscriptionType'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
    ]
from django.db import models
from users.models import *
from venues.models import * 

# Create your models here.
class SubscriptionType(models.Model):
    SUBSCRIPTION_TYPES = (
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra large"),
        ("E", "Enterprise")
    )
    name = models.CharField(max_length=5, choices=SUBSCRIPTION_TYPES)
    daily_allowed_scans = models.IntegerField()
    default_cost = models.DecimalField(max_digits=100, decimal_places=2)
    def __str__(self):
        return self.name + ": " + str(self.daily_allowed_scans)

class Subscription(models.Model):
    type = models.ForeignKey(SubscriptionType, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(Account, related_name="subscriptions", on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True)
    TERM_LENGTHS = (
        ("1w", "1 week"),
        ("1m", "1 month"),
        ("3m", "3 months"),
        ("6m", "6 months"),
        ("1y", "1 year")
    )
    term_length = models.CharField(max_length=4, choices=TERM_LENGTHS)
    next_renewal = models.DateTimeField()
    cost = models.DecimalField(max_digits=100, decimal_places=2)
    coupon_code = models.CharField(max_length=20)
    def __str__(self):
        return str(self.user) + " Subscription"

class Transaction(models.Model):
    subscription = models.ForeignKey(Subscription, related_name="transactions", on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=120)
    order_id = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    success = models.BooleanField(default=True)
    def __str__(self):
        return self.order_id 
    class Meta:
        ordering = ['-date_created']

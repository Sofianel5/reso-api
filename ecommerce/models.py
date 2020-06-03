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
    daily_allowed_scans = models.IntegerField(blank=True, null=True)
    default_cost = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)

    @property
    def human_readable_name(self):
        return [i for i in self.SUBSCRIPTION_TYPES if i[0] == self.name][0][1]

    def __str__(self):
        return self.name + ": " + str(self.daily_allowed_scans)


class Subscription(models.Model):
    type = models.ForeignKey(SubscriptionType, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(Account, related_name="subscriptions", on_delete=models.DO_NOTHING)
    date_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
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


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField(null=True, blank=True)
    percent_off = models.FloatField(null=True, blank=True)

    @property
    def is_amount(self):
        return self.amount is not None

    def __str__(self):
        return self.code


class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.DO_NOTHING)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, blank=True, null=True
    )
    transaction = models.ForeignKey(
        Transaction, on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True
    )
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    class Meta:
        ordering = ['-ordered_date']


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"

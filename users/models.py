from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone 
from django.contrib.auth.validators import UnicodeUsernameValidator 
from django.utils.translation import ugettext_lazy as _ 
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager 
from .managers import AccountManager 
from datetime import datetime, timedelta
from django.utils import timezone 
import uuid
from geolocation.models import Coordinates, Address

class Account(AbstractBaseUser):
    username = None 
    email = models.EmailField(verbose_name=_("Email"), max_length=150, unique=True)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4)
    date_joined = models.DateTimeField(verbose_name=_("date joined"), auto_now_add=True)
    first_name = models.CharField(verbose_name=_("First name"), max_length=100)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=100)
    coordinates = models.ForeignKey(Coordinates, on_delete=models.DO_NOTHING, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_venueadmin = models.BooleanField(default=False)
    last_login = models.DateTimeField(verbose_name=_("Last login"), auto_now=True)
    is_locked = models.BooleanField(default=True)
    objects = AccountManager()

    # When they first enter into a venue, calculate a new starting value by just taking the venue's value
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    def __str__(self):
        return self.first_name + " " + self.last_name 

    def has_perm(self, perm, obj=None):
        return self.is_active 

    def has_module_perms(self, app_label):
        return True

    @property 
    def full_name(self):
        return self.__str__()
    
    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)


class PeerToVenueHandshake(models.Model):
    person = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name="handshakes")
    venue = models.ForeignKey("venues.Venue", on_delete=models.DO_NOTHING, related_name="handshakes")
    time = models.DateTimeField(auto_now_add=True)
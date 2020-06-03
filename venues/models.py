import logging
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from timezonefinder import TimezoneFinder

from geolocation.models import Coordinates, Address
from users.models import Account

db_logger = logging.getLogger('db')


# Create your models here.
class Venue(models.Model):
    VENUE_TYPES = [
        ("Resturaunt", _("Resturaunt")),
        ("Grocery", _("Grocery")),
        ("Coffee", _("Coffee")),
        ("Gym", _("Gym")),
        ("Gas", _("Gas")),
        ("Mail", _("Mail")),
        ("Laundry", ("Laundry")),
        ("Repair", _("Repair")),
        ("Beauty", _("Beauty")),
        ("Education", _("Education")),
    ]
    type = models.CharField(max_length=20, choices=VENUE_TYPES)
    description = models.CharField(max_length=128, blank=True, null=True)
    admin = models.ForeignKey("users.Account", on_delete=models.DO_NOTHING, null=True, blank=True,
                              related_name="venues")
    title = models.CharField(max_length=50)
    coordinates = models.ForeignKey(Coordinates, null=True, blank=True, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING, null=True, related_name="venue")
    timezone = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(default="venues/default.jpg", upload_to="venues")
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    capacity = models.IntegerField()
    website = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.coordinates is None:
            self.coordinates = self.address.to_coordinates()
        elif self.address is None:
            self.address = self.coordinates.to_address()
        tf = TimezoneFinder()
        latitude, longitude = (self.coordinates.lat, self.coordinates.lng)
        timezone = tf.timezone_at(lng=longitude, lat=latitude)
        self.timezone = timezone
        super(Venue, self).save(*args, **kwargs)

    def bookable_time_slots(self):
        now = datetime.now()
        timeslots = self.time_slots.filter(stop__gte=now)
        return timeslots

    def current_timeslots(self):
        now = datetime.now()
        timeslots = self.time_slots.filter(start__lte=now, stop__gte=now)
        return timeslots

    def current_timeslot(self):
        return self.current_timeslot.all()[0]


class TimeSlot(models.Model):
    TYPES = [
        ("All", _("All")),
        ("Eldery", _("Elderly")),
        ("Frontline", _("Frontline")),
    ]
    venue = models.ForeignKey(Venue, on_delete=models.DO_NOTHING, related_name="time_slots")
    start = models.DateTimeField()
    stop = models.DateTimeField()
    max_attendees = models.IntegerField(_("Max attendees"))
    type = models.CharField(max_length=25, choices=TYPES, default="All")
    attendees = models.ManyToManyField(Account, blank=True, related_name="time_slots")
    external_attendees = models.IntegerField(default=0)
    attending = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super(TimeSlot, self).save(*args, **kwargs)

    @property
    def num_attendees(self):
        return self.attendees.count() + self.external_attendees

    def add_attendee(self, attendee):
        assert (self.stop > datetime.now())
        assert (attendee not in self.attendees.all())
        if self.num_attendees < self.max_attendees:
            self.attendees.add(attendee)
            self.save()
            return True
        else:
            raise Exception

    def add_external_attendee(self):
        if self.num_attendees + 1 <= self.max_attendees:
            self.external_attendees += 1
            self.save()
        else:
            raise Exception

    def remove_external_attendee(self):
        if self.external_attendees > 0:
            self.external_attendees -= 1
            self.save()
        raise Exception

    def record_attending(self, num):
        if self.attending + num > 0:
            self.attending += num
            self.save()
        else:
            raise Exception

    def clear_attendees(self):
        self.attendees = 0
        self.save()

    @property
    def current(self):
        now = datetime.now()
        return self.start < now and self.stop > now

    @property
    def past(self):
        now = datetime.now()
        return self.stop < now

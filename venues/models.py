from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Account
from datetime import datetime, timedelta
import uuid
from timezonefinder import TimezoneFinder
import pytz
from geolocation.models import Coordinates, Address
import logging
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
    admin = models.ForeignKey("users.Account", on_delete=models.DO_NOTHING, null=True, blank=True, related_name="venues")
    title = models.CharField(max_length=50)
    coordinates = models.ForeignKey(Coordinates, null=True, blank=True, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING, null=True, related_name="venue")
    timezone = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(default="venues/default.jpg", upload_to="venues")
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.CharField(max_length=128, blank=True, null=True)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        db_logger(self.coordinates)
        if self.coordinates is None:
            db_logger.info("coordinates is none")
            self.coordinates = self.address.to_coordinates()
        elif self.address is None:
            db_logger.info("coordinates is not none")
            self.address = self.coordinates.to_address()
        db_logger.info(self.coordinates)
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

    @property
    def num_attendees(self):
        return self.attendees.count()

    def add_attendee(self, attendee):
        assert(self.stop > datetime.now())
        assert(attendee not in self.attendees.all())
        if self.attendees.count() < self.max_attendees:
            self.attendees.add(attendee)
            self.save()
            return True 
        raise Exception

    @property 
    def current(self):
        utc = pytz.utc
        now = utc.localize(datetime.now())
        try:
            start = utc.localize(self.start)
        except:
            start = self.start
        try:
            stop = utc.localize(self.stop)
        except:
            stop = self.stop
        return start < now and stop > now
    
    @property
    def past(self):
        utc = pytz.utc
        now = utc.localize(datetime.now())  
        try:
            stop = utc.localize(self.stop)
        except:
            stop = self.stop
        return stop < now

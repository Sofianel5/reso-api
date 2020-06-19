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
        ("Retail", _("Retail")),
        ("Restaurant", _("Restaurant")),
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
    capacity = models.IntegerField()
    attendee_count = models.IntegerField(default=0)
    visit_length = models.IntegerField()
    website = models.CharField(max_length=128, blank=True, null=True)
    visible = models.BooleanField(default=True)
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
        ts = self.current_timeslots()
        if (ts.count() > 0):
            return self.current_timeslots().all()[0] 
        return None
    
    def get_attendee_count(self):
        if self.current_timeslot() != None:
            return self.current_timeslot().attending + self.attendee_count
        return self.attendee_count
    
    def clear_attendees(self):
        if self.current_timeslot() != None:
            self.current_timeslot().clear_attendees() 
        self.attendee_count = 0
        self.save()
    
    def increment_attendees(self, num):
        if self.current_timeslot() != None:
            if self.current_timeslot().attending + num >= 0:
                self.current_timeslot().record_attending(num) 
                return
        if self.attendee_count + num >= 0:
            self.attendee_count += num
            self.save()
    
    def generate_month(self):
        self.schedule.generate_month()

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
        assert(self.stop > datetime.now())
        assert(attendee not in self.attendees.all())
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
        else:
            raise Exception

    def record_attending(self, num):
        if self.attending + num >= 0:
            self.attending += num
            self.save()
        else:
            raise Exception
    
    def clear_attendees(self):
        self.attending = 0
        self.save()
    
    @property
    def is_bookable(self):
        return self.num_attendees <= self.max_attendees
        
    @property 
    def current(self):
        now = datetime.now()
        return self.start < now and self.stop > now

    @property
    def past(self):
        now = datetime.now()
        return self.stop < now

    def __str__(self):
        return "%s: from %s to %s" % (str(self.venue), self.start.strftime('%m/%d %H:%M:%S'), self.stop.strftime('%m/%d %H:%M:%S'))

class ScheduleDay(models.Model):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    DAYS = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday")
    )
    index = models.IntegerField(choices=DAYS)
    start_hour = models.IntegerField()
    start_minute = models.IntegerField()
    stop_hour = models.IntegerField()
    stop_minute = models.IntegerField()
    def __str__(self):
        return "%s, %i:%i to %i:%i" % (self.get_index_display(), self.start_hour, self.start_minute, self.stop_hour, self.stop_minute)

class Schedule(models.Model):
    weekdays = models.ManyToManyField(ScheduleDay)
    interval_length = models.IntegerField()
    venue = models.OneToOneField(Venue, on_delete=models.CASCADE)

    def generate_continous(self, startt, endt, interval, venuet, mt, type1="All"):
        counter = startt
        while (counter < endt):
            temp = TimeSlot.objects.create(venue=venuet, start=counter,stop=(counter + timedelta(minutes = interval)), max_attendees = mt, type = type1)
            temp.save()
            print(temp)
            counter += timedelta(minutes = interval)
    
    @property 
    def days_open(self):
        return [day.index for day in self.weekdays.all()]
    
    def get_day(self, idx):
        for day in self.weekdays.all():
            if day.index == idx:
                return day
    
    def generate(self, start, stop):
        while (start < stop):
            if start.weekday() + 1 in self.days_open:
                day = self.get_day(start.weekday()+1)
                self.generate_continous(
                    start.replace(hour=day.start_hour, minute=day.start_minute), 
                    start.replace(hour=day.stop_hour, minute=day.stop_hour),
                    self.venue.visit_length,
                    self.venue,
                    self.venue.capacity
                )
            start += timedelta(days=1)
    
    def generate_month(self):
        start = datetime.today()
        stop =  start+timedelta(days=30)
        self.generate(start, stop)
    def __str__(self):
        return "Schedule for %s" % (str(self.venue))



    
    

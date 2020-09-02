from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import Account
from datetime import datetime, timedelta
import uuid
from timezonefinder import TimezoneFinder
import pytz
from geolocation.models import Coordinates, Address
from django.core.mail import send_mail, EmailMultiAlternatives
from .utils import create_dynamic_link
import logging
db_logger = logging.getLogger('db')

class Venue(models.Model): 
    VENUE_TYPES = [
        ("Retail", _("Retail")),
        ("Real Estate", _("Real Estate")),
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
    lead_time_hours = models.FloatField(default=0)
    requires_form = models.BooleanField(default=False)
    form_url = models.CharField(max_length=1000, blank=True, null=True)
    mask_required = models.BooleanField(default=True)
    share_link = models.URLField(max_length=200, blank=True, null=True)
    allows_named_attendees = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    def local_time_naive(self):
        return datetime.now(pytz.timezone(self.timezone)).replace(tzinfo=None)

    def save(self, *args, **kwargs):
        if self.coordinates is None:
            self.coordinates = self.address.to_coordinates()
        elif self.address is None:
            self.address = self.coordinates.to_address()
        tf = TimezoneFinder()
        latitude, longitude = (self.coordinates.lat, self.coordinates.lng)
        timezone = tf.timezone_at(lng=longitude, lat=latitude)
        self.timezone = timezone
        if self.share_link is None:
            self.share_link = create_dynamic_link(
                "https://api.tracery.us/venues/share/", 
                {"venue": self.pk},
                f"Click to book your private viewing at {self.title} on The Reso App",
                self.description,
                self.image.url
            )
        if self.admin.share_link is None:
            self.admin.share_link = create_dynamic_link(
                "https://api.tracery.us/users/share/",
                {"user": self.admin.pk},
                f"View {self.admin}'s listings on The Reso App",
                "Click to book your private viewings on The Reso App.",
                self.admin.profile_picture.url
            )
            self.admin.save()
        super(Venue, self).save(*args, **kwargs)

    def bookable_time_slots(self):
        now = self.local_time_naive()
        timeslots = self.time_slots.filter(stop__gte=now)
        return timeslots

    def current_timeslots(self):
        now = self.local_time_naive()
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
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super(TimeSlot, self).save(*args, **kwargs)

    @property
    def num_attendees(self):
        return self.attendees.count() + self.external_attendees
    
    def send_user_form_email(self, attendee):
        subject = "Form to be admitted entry to " + self.venue.title 
        from_email = "The Reso App <accounts@tracery.us>"
        to_email = attendee.email 
        text_content = f"""Hello, in order to be admitted into {self.venue.title}, the law requires you to complete this form.
        {self.venue.form_url}
        Please reply to this email with your completed form so that {self.venue.title} can allow you to visit.
        Best,
        The Reso App Team
        """
        html_content = f""" 
        <h5>Hello, {attendee.full_name}</h5>
        <p>
        In order to be admitted into {self.venue.title}, the law requires you to complete <a href="{self.venue.form_url}">this form.</a>
        </p>
        <p>
        Please reply to this email with your completed form so that {self.venue.title} can allow you to visit.
        </p>
        <p>
        Best,<br>
        The Reso App Team
        </p>
        """
        message = EmailMultiAlternatives(subject, text_content, from_email, [to_email], bcc=[self.venue.admin.email], reply_to=[self.venue.admin.email])
        message.attach_alternative(html_content, "text/html")
        message.send(fail_silently=False)
    
    def send_admin_attendee_email(self, attendee):
        subject = "Someone just registered to visit your venue"
        from_email = "The Reso App <accounts@tracery.us>"
        to_email = self.venue.admin.email 
        text_content = f"""Hello {self.venue.admin.full_name},
The Reso App user {attendee.full_name} just registered to visit {self.venue.title} from {self.start.strftime('%m/%d %-I:%M %p')} to {self.stop.strftime('%m/%d %-I:%M %p')}.
We emailed them the form they need to submit, and bcced you on the email. When they reply, their response will be sent to you.
Best,
The Reso App Team
        """
        message = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        message.send()

    def add_attendee(self, attendee):
        assert(self.stop > self.venue.local_time_naive())
        assert(attendee not in self.attendees.all())
        if self.num_attendees < self.max_attendees:
            self.attendees.add(attendee)
            self.save()
            if self.venue.requires_form:
                self.send_user_form_email(attendee)
                self.send_admin_attendee_email(attendee)
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
        now = self.venue.local_time_naive()
        return self.start < now and self.stop > now

    @property
    def past(self):
        now = self.venue.local_time_naive()
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
    TYPES = [
        ("All", _("All")),
        ("Eldery", _("Elderly")),
        ("Frontline", _("Frontline")),
    ]
    type = models.CharField(max_length=25, choices=TYPES, default="All")
    venue = models.OneToOneField(Venue, on_delete=models.CASCADE)
    def generate_continous(self, startt, endt, interval, venuet, mt):
        counter = startt
        while (counter < endt):
            temp = TimeSlot.objects.create(venue=venuet, start=counter,stop=(counter + timedelta(minutes = interval)), max_attendees = mt, type = self.type)
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



    
    

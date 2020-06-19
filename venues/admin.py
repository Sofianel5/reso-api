from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Venue)
admin.site.register(Coordinates)
admin.site.register(Address)
admin.site.register(TimeSlot)
admin.site.register(Schedule)
admin.site.register(ScheduleDay)
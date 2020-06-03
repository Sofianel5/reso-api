from django.contrib import admin

from .models import Venue, Coordinates, Address, TimeSlot

# Register your models here.
admin.site.register(Venue)
admin.site.register(Coordinates)
admin.site.register(Address)
admin.site.register(TimeSlot)

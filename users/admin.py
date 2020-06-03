from django.contrib import admin

from .models import Account, PeerToVenueHandshake

# Register your models here.
admin.site.register(Account)
admin.site.register(PeerToVenueHandshake)

from django.contrib import admin
from .models import Account, PeerToVenueHandshake
# Register your models here.
admin.site.register(Account)
admin.site.register(PeerToVenueHandshake)
admin.site.site_header = "RetailReso Administration"
admin.site.site_title = "RetailReso Administration"
admin.site.index_title = "RetailReso Administration"
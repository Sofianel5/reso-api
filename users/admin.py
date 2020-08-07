from django.contrib import admin
from .models import Account, PeerToVenueHandshake
# Register your models here.
admin.site.register(Account)
admin.site.register(PeerToVenueHandshake)
admin.site.site_header = "Reso Administration"
admin.site.site_title = "Reso Administration"
admin.site.index_title = "Reso Administration"
import uuid

from django.db import models

from users.models import PeerToVenueHandshake


# Create your models here.
class HandshakeRequestFromVenue(models.Model):
    _from = models.ForeignKey("venues.Venue", on_delete=models.CASCADE)
    _to = models.ForeignKey("users.Account", on_delete=models.CASCADE)
    from_confirmed = models.BooleanField(default=False)
    to_confirmed = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    thread_id = models.UUIDField(default=uuid.uuid4, unique=True)

    @property
    def is_valid(self):
        return self.from_confirmed and self.to_confirmed

    @property
    def venue(self):
        return self._from

    @property
    def user(self):
        return self._to

    def __str__(self):
        return "From(venue) " + self._from.__str__() + " to " + self._to.__str__()

    def confirm(self):
        handshake = PeerToVenueHandshake.objects.create(venue=_from, person=_to)
        handshake.save()
        self.delete()

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from venues.models import Venue, TimeSlot
from users.models import Account, PeerToVenueHandshake
from .models import *
from geolocation.models import Coordinates, Address

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('email', 'first_name', 'last_name', 'password')

class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account 
        exclude = ["password", "last_login", "email", "date_joined", "id", "public_id", "is_active", "is_locked", "is_venueadmin", "is_staff", "is_admin"]


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        exclude = ['admin', 'email', 'phone', 'website']
        depth = 1

class TimeSlotSerializer(serializers.ModelSerializer):
    venue = VenueSerializer()
    class Meta:
        model = TimeSlot 
        fields = ['start', 'stop', 'max_attendees', 'num_attendees', 'id', 'current', 'past', 'venue']
        
class VenueDetailSerializer(serializers.ModelSerializer):
    admin = ExternalAccountSerializer()
    #time_slots = TimeSlotSerializer(many=True)
    class Meta:
        model = Venue
        fields = "__all__"
        depth = 1

class InternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ["password"]
        depth = 2

class HandshakeRequestFromVenueSerializer(serializers.ModelSerializer):
    _from = VenueSerializer()
    _to = ExternalAccountSerializer()
    class Meta:
        model = HandshakeRequestFromVenue
        fields = "__all__"
        depth = 2
